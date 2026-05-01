def get_linkedin_data(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        # УДАЛЯЕМ Service(ChromeDriverManager().install())
        # Просто запускаем драйвер. В среде Nixpacks он уже прописан в PATH
        driver = webdriver.Chrome(options=chrome_options)
        
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        
        # Остальной код...
        title_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.top-card-layout__title, .topcard__title, h1")))
        company = "Не найдена"
        try:
            comp_el = driver.find_element(By.CSS_SELECTOR, "a.topcard__org-name-link, .topcard__flavor a")
            company = comp_el.text.strip()
        except:
            pass

        return {"title": title_el.text.strip(), "company": company}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if 'driver' in locals():
            driver.quit()
