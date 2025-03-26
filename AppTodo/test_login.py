from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class TestLogin:

    def setup_class(self):
        global driver
        driver = webdriver.Chrome() # Configurar o navegador (exemplo com Chrome)
        driver.maximize_window()

    def test_login(self):
        # Abrir a aplicação Appsmith
        driver.get("https://app.appsmith.com/app/todo-app/home-67d302b60471e20112f45cdc?branch=master")

        # Aguardar a página carregar completamente
        time.sleep(3)

        # Clicar no botão de login antes de preencher os campos
        login_button = driver.find_element(By.CLASS_NAME, "jTidbG")
        login_button.click()
        time.sleep(2)  # Aguardar abertura do formulário de login

        # Encontrar os campos de entrada
        input_fields = driver.find_elements(By.CLASS_NAME, "bp3-input")

        if len(input_fields) >= 2:
            input_fields[0].send_keys("joaoferreira")  # Username
            input_fields[1].send_keys("joaoferreira@")  # Senha
        else:
            print("Campos de entrada não encontrados!")

        # Encontrar e clicar no botão de login após preencher os dados
        login_button_final = driver.find_element(By.CLASS_NAME, "fuGmKe")
        login_button_final.click()

        # Esperar carregamento da página após login
        time.sleep(3)

        # Verificar se a mensagem de sucesso aparece
        success_message = driver.find_element(By.CLASS_NAME, "dmRUro")

        print(success_message.text)

        assert 'Login successfull' in success_message.text

    def teardown_class(self):
        driver.quit() # Fechar o navegador
