import threading
from io import BytesIO

import requests
from PIL import Image
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup


def extract_real_image(url):
    if "imageproxy/" in url:
        return url.split("imageproxy/")[-1].split("?")[0]
    return url


def fetch_courses_from_search(query, limit=10):
    results = []
    page = 1

    while len(results) < limit:
        url = f"https://www.coursera.org/courses?query={query}&page={page}"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        # 🔥 Target ALL course cards
        items = soup.find_all("li")

        for item in items:
            try:
                # -------------------
                # THUMBNAIL
                # -------------------
                img_tag = item.find("img")

                if not img_tag:
                    continue

                thumbnail = img_tag.get("src")

                if not thumbnail:
                    continue  # ❌ skip if no image

                # -------------------
                # COURSE LINK
                # -------------------
                link_tag = item.find("a", href=True)

                if not link_tag:
                    continue

                href = link_tag["href"]

                if "/learn/" not in href:
                    continue

                slug = href.split("/learn/")[-1].split("/")[0]

                if not slug:
                    continue

                results.append({
                    "slug": slug,
                    "thumbnail": extract_real_image(thumbnail)
                })

            except Exception:
                continue

            if len(results) >= limit:
                break

        page += 1

        # safety break
        if page > 10:
            break

    return results[:limit]


import random
from decimal import Decimal
from django.contrib.auth import get_user_model

User = get_user_model()


def assign_mentor_and_price():
    mentors = User.objects.filter(role="mentor")

    mentor = random.choice(mentors) if mentors.exists() else None

    # Pricing logic
    is_free = random.choice([True, False])

    if is_free:
        price = Decimal("0.00")
    else:
        price = Decimal(random.choice([499, 999, 1499, 1999]))

    return mentor, is_free, price


import requests
from bs4 import BeautifulSoup
from django.utils.text import slugify

from .models import Course, Category, Tag, Unit


def create_course_from_slug(slug, thumbnail_url):
    try:
        url = f"https://www.coursera.org/learn/{slug}"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        # ---------------------------
        # BASIC INFO
        # ---------------------------

        title_tag = soup.find("h1")
        title = title_tag.text.strip() if title_tag else slug

        desc_tag = soup.find("meta", {"name": "description"})
        description = desc_tag["content"] if desc_tag else ""

        short_description = description[:250]

        # ---------------------------
        # CATEGORY
        # ---------------------------

        category_name = "General"
        print("works till this")

        breadcrumb = soup.find_all("a")
        for a in breadcrumb:
            if "browse" in a.get("href", ""):
                category_name = a.text.strip()
                break

        category, _ = Category.objects.get_or_create(
            name=category_name,
            defaults={"slug": slugify(category_name)}
        )

        # ---------------------------
        # TAGS
        # ---------------------------
        print("tags are getting fetched")

        tag_objs = []

        skills_ul = soup.find("ul", {"data-testid": "skills-section"})

        if skills_ul:
            skill_links = skills_ul.find_all("a")

            for skill in skill_links[:10]:  # limit to 10 tags
                tag_name = skill.text.strip()

                if not tag_name:
                    continue

                obj, _ = Tag.objects.get_or_create(
                    name=tag_name,
                    defaults={"slug": slugify(tag_name)}
                )

                tag_objs.append(obj)

        print("tags are fetched")

        # ---------------------------
        # MENTOR + PRICING
        # ---------------------------

        mentor, is_free, price = assign_mentor_and_price()

        if not mentor:
            print("❌ No mentor found")
            return

        # ---------------------------
        # CREATE COURSE
        # ---------------------------

        course_obj, created = Course.objects.get_or_create(
            slug=slug,
            defaults={
                "title": title,
                "short_description": short_description,
                "description": description,
                "category": category,
                "mentor": mentor,
                "level": "beginner",
                "status": "published",
                "is_free": is_free,
                "price": price,
                "duration_hours": 10,
            }
        )

        if tag_objs:
            course_obj.keywords.add(*tag_objs)

        # ---------------------------
        # THUMBNAIL (FIXED)
        # ---------------------------
        print('thumbnail processing')

        if thumbnail_url and not course_obj.thumbnail:
            try:
                img = requests.get(thumbnail_url).content
                # course_obj.thumbnail = Image.open(BytesIO(img))
                course_obj.thumbnail.save(f"{slug}.jpg", content=BytesIO(img), save=True)
            except Exception as e:
                print('thumbnail failed')
                print('thumbnail failed')
                print(e)

        # ---------------------------
        # MODULES → UNITS (WITH DESC)
        # ---------------------------

        modules = soup.find_all("div")
        print('unit time')

        order = 1
        for m in modules:
            title_tag = m.find("h3")
            desc_tag = m.find("p")

            if not title_tag:
                continue

            title = title_tag.text.strip()
            desc = desc_tag.text.strip() if desc_tag else ""

            if not title:
                continue

            Unit.objects.get_or_create(
                course=course_obj,
                order=order,
                defaults={
                    "title": title,
                    "description": desc,
                    "is_preview": order == 1,
                    "is_locked": order != 1,
                }
            )

            order += 1

        print(f"✅ Created: {course_obj.title}")

    except Exception as e:
        print(f"❌ Error: {e}")


def main(query, limit=10):
    courses = fetch_courses_from_search(query, limit)

    for c in courses:
        threading.Thread(target=create_course_from_slug, args=(c["slug"], c["thumbnail"])).start()
