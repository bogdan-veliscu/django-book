from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from factories import UserFactory
import logging
logger = logging.getLogger(__name__)

class TestArticleCreation(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        firefox_options = webdriver.FirefoxOptions()
        cls.selenium = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            options=firefox_options
        )
        cls.selenium.implicitly_wait(10)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_create_article(self):
        user = UserFactory(email='testuser@email.com', password='securepassword123')
        logger.debug(f"User: {user}")
        
        breakpoint()
        self.selenium.get(f'{self.live_server_url}/login')
        logger.debug(f"URL: {self.live_server_url}/login")
        username_field = self.selenium.find_element(By.ID, "input-username-for-credentials-provider")
        username_field.send_keys(user.email)
        self.selenium.find_element(By.ID, "input-password-for-credentials-provider").send_keys(user.password)
        logger.info("Logging in")
        self.selenium.find_element(By.NAME, "password").send_keys(Keys.RETURN)

        # Navigate to article creation page
        WebDriverWait(self.selenium, 10).until(EC.url_changes(f'{self.live_server_url}/'))
        logger.info("Logged in")
        self.selenium.get(f'{self.live_server_url}/posts/create')
        logger.info("Navigating to create article page")

        # Fill out the article creation form
        self.selenium.find_element(By.NAME, "title").send_keys("Selenium Test Article")
        self.selenium.find_element(By.NAME, "description").send_keys("Description for the Selenium test article.")
        self.selenium.find_element(By.NAME, "body").send_keys("Content for the Selenium test article.")
        logger.info("Filling out the article creation form")
        self.selenium.find_element(By.NAME, "submit").click()
        logger.info("Submitting the form")

        # Verify the article was created
        WebDriverWait(self.selenium, 10).until(EC.url_contains('/posts/'))
        assert "Selenium Test Article" in self.selenium.page_source
