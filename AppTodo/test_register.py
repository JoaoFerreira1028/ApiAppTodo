from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class TestRegistar:

    def setup_class(self):
        global driver
        driver = webdriver.Chrome() # Configurar o navegador (exemplo com Chrome)
        driver.maximize_window()

    def test_register(self):
        # Abrir a aplicação Appsmith
        driver.get("https://app.appsmith.com/app/todo-app/home-67d302b60471e20112f45cdc?branch=master")

        # Aguardar a página carregar completamente
        time.sleep(3)

        # Clicar no botão de registar antes de preencher os campos
        register_button = driver.find_elements(By.CLASS_NAME, "jTidbG")
        register_button[1].click()
        time.sleep(2)  # Aguardar abertura do formulário de registar

        # Encontrar os campos de entrada
        input_fields = driver.find_elements(By.CLASS_NAME, "bp3-input")

        input_fields[0].send_keys("joaomarinhas")  # Username
        input_fields[1].send_keys("Joao Marinhas")  # Fullname
        input_fields[2].send_keys("joaomarinhas@example.com")  # Email
        input_fields[3].send_keys("joaomarinhas@")  # Senha

        # Encontrar e clicar no botão de registar após preencher os dados
        register_button_final = driver.find_element(By.CLASS_NAME, "fuGmKe")
        register_button_final.click()

        # Esperar carregamento da página após registar
        time.sleep(3)

        # Verificar se a mensagem de sucesso aparece
        success_message = driver.find_element(By.CLASS_NAME, "dmRUro")

        print(success_message.text)

        assert 'User created' in success_message.text

    def teardown_class(self):
        driver.quit() # Fechar o navegador
