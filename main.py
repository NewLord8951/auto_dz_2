import os
from loguru import logger
from dotenv import find_dotenv, load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
load_dotenv(find_dotenv())

# Логин
L = os.getenv('L')
# Пароль
P = os.getenv('P')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://journal.top-academy.ru/")
    page.wait_for_selector('input[name="username"]', timeout=1000)
    page.fill('input[name="username"]', L)
    page.fill('input[name="password"]', P)
    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)
    page.goto("https://journal.top-academy.ru/main/homework/page/index")
    try:
        page.click('line[x1="25"][x2="11"][y1="11"][y2="25"]')
    except:
        pass
    page.wait_for_selector('.homework-item', timeout=1000)
    now = 0
    maximum = 100
    processed_count = 0
    try:
        try:
            page.wait_for_selector(".error-text", state="visible", timeout=1000)
        except PlaywrightTimeout:
            pass
        star = page.locator('span.bs-rating-star[title="5"]')
        if star.is_visible():
            star.click()
        page.get_by_role("button", name="Далее").click()
        star2 = page.locator('span.bs-rating-star[title="5"]')
        if star2.is_visible():
            star2.click()  
        page.get_by_role("button", name="Отправить")
    except:
        pass  
    while now < maximum:
        try:
            homework_items = page.query_selector_all('.homework-item')
            if len(homework_items) == 0:
                logger.info("Больше нет домашних заданий для обработки")
                break
            found_active = False
            for index, homework_item in enumerate(homework_items):
                try:
                    upload_button = homework_item.query_selector('.upload-file img[src*="upload.png"]')       
                    if upload_button:
                        subject_element = homework_item.query_selector('.name-spec')
                        subject_name = subject_element.inner_text() if subject_element else f"Задание {index + 1}"
                        homework_item.hover()
                        page.wait_for_timeout(1000)
                        upload_button.click()
                        page.wait_for_timeout(1000)
                        field = page.locator('span.text-homework-field[contenteditable]')
                        field.click()
                        field.fill("https://github.com/NewLord8951")
                        try:
                            star_buttons = [
                                '.bs-rating-star[title="5"] .rating-star',
                                '.bs-rating-star[title="4"] .rating-star', 
                                '.bs-rating-star[title="3"] .rating-star',
                                '.bs-rating-star[title="2"] .rating-star',
                                '.bs-rating-star[title="1"] .rating-star',
                                '.rating-star',
                                '.bs-rating-star button'
                            ]
                            for star_selector in star_buttons:
                                try:
                                    page.wait_for_selector(star_selector, timeout=1000)
                                    page.click(star_selector)
                                    break
                                except:
                                    continue       
                            page.wait_for_timeout(1000)
                            try:
                                hours_input = page.wait_for_selector('input[placeholder="чч"]', timeout=3000)
                                hours_input.click()
                                hours_input.fill('0')
                                page.wait_for_timeout(500)
                                minutes_input = page.wait_for_selector('input[placeholder="мм"]', timeout=3000)
                                minutes_input.click()
                                minutes_input.fill('30')
                                page.wait_for_timeout(500)
                            except:
                                pass     
                        except Exception as rating_error:
                            logger.warning(f"Ошибка при установке рейтинга: {rating_error}")
                        try:
                            submit_buttons = [
                                'button.btn.btn-accept:has-text("Отправить")',
                                'button:has-text("Отправить")',
                                '.btn-accept',
                                'button[class*="accept"]'
                            ]
                            for submit_selector in submit_buttons:
                                try:
                                    submit_btn = page.wait_for_selector(submit_selector, timeout=3000)
                                    if submit_btn and submit_btn.is_visible():
                                        submit_btn.click()
                                        page.wait_for_timeout(5000)
                                        try:
                                            page.wait_for_selector('.modal', state='hidden', timeout=5000)
                                        except:
                                            page.keyboard.press('Escape')
                                            page.wait_for_timeout(1000)
                                        break
                                except:
                                    continue
                            else:
                                page.keyboard.press('Escape')
                                page.wait_for_timeout(1000)
                        except Exception as submit_error:
                            logger.warning(f"Не удалось нажать кнопку 'Отправить': {submit_error}")
                            try:
                                page.keyboard.press('Escape')
                                page.wait_for_timeout(1000)
                            except:
                                pass
                        processed_count += 1
                        found_active = True
                        break 
                except Exception as e:
                    logger.error(f"Ошибка при обработке задания {index + 1}: {e}")
                    try:
                        page.keyboard.press('Escape')
                        page.wait_for_timeout(1000)
                    except:
                        pass
                    continue 
            if not found_active:
                break
            page.wait_for_timeout(3000)
            now += 1
        except Exception as e:
            logger.error(f"Общая ошибка в цикле обработки: {e}")
            break
input("Нажмите Enter для закрытия...")
browser.close()