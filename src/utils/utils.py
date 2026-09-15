import ctypes
import webbrowser
import customtkinter as ctk
import re
import hashlib
import hmac
import os

PBKDF2_ITERATIONS = 200_000


def hash_password(password: str) -> str:
    """Gera o hash da senha com PBKDF2-HMAC-SHA256 e salt aleatório.

    Formato gravado: pbkdf2_sha256$<iterações>$<salt hex>$<hash hex>
    """
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${derived.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Compara a senha digitada com o hash gravado, em tempo constante.

    Aceita o formato novo (PBKDF2 com salt) e, para bancos criados antes desta
    versão, o formato antigo (SHA-256 puro em hex).
    """
    if not stored:
        return False
    if stored.startswith("pbkdf2_sha256$"):
        try:
            _, iterations, salt_hex, hash_hex = stored.split("$")
            derived = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                bytes.fromhex(salt_hex),
                int(iterations),
            )
        except (ValueError, TypeError):
            return False
        return hmac.compare_digest(derived.hex(), hash_hex)
    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy, stored)


class Utilities:

    def __init__(self) -> None:
        pass

    @staticmethod
    def msgbox(title, text, style):
        #  Styles:
        #  0 : OK
        #  1 : OK | Cancel
        #  2 : Abort | Retry | Ignore
        #  3 : Yes | No | Cancel 6, 7, 2
        #  4 : Yes | No
        #  5 : Retry | Cancel
        #  6 : Cancel | Try Again | Continue

        return ctypes.windll.user32.MessageBoxW(0, text, title, style)

    @staticmethod
    def open_website(url):
        # URL do site que deseja abrir
        website_url = url
        # Abrir o site no navegador padrão
        webbrowser.open(website_url)

    @staticmethod
    def restart_interface(frame):
        # Destruir todos os widgets existentes
        for widget in frame.winfo_children():
            widget.destroy()

    def validate_username_strength(self, username):
        # Verifica se o nome de usuário tem pelo menos 3 e no máximo 20 caracteres
        if not 3 <= len(username) <= 20:
            return False

        # Verifica se o nome de usuário contém apenas letras e números
        if not re.match(r"^[a-zA-Z0-9]+$", username):
            return False

        # Verifica se o nome de usuário não começa ou termina com espaços em branco
        if username.strip() != username:
            return False

        return True

    def format_username_label(self, label, text, is_valid):
        if is_valid:
            label.configure(text=text[0], text_color="green")
        else:
            label.configure(text=text[1], text_color="red")

    def validate_password_strength(self, password):
        if (
            len(password) >= 6
            and any(char.isalpha() for char in password)
            and any(char.isdigit() for char in password)
            and any(char in "!$@%#" for char in password)
        ):
            return True
        else:
            return False

    def format_password_label(self, label, text, is_valid):
        if is_valid:
            label.configure(text=text[0], text_color="green")
        else:
            label.configure(text=text[1], text_color="red")

    def validate_password_match(self, password, confirmation):
        if password == confirmation and password != "" and confirmation != "":
            return bool

    def validate_password(
        self,
        password_entry,
        confirmation_entry,
        password_text,
        confirmation_text,
        event=None,
    ):

        is_valid_password = self.validate_password_strength(password_entry)
        is_valid_confirmation = self.validate_password_match(
            password_entry, confirmation_entry
        )

        self.format_password_label(
            password_text, ["Senha válida", "Senha inválida"], is_valid_password
        )
        self.format_password_label(
            confirmation_text,
            ["Senhas Iguais", "Senhas Diferentes"],
            is_valid_confirmation,
        )

        if is_valid_confirmation and is_valid_password:
            return True

    def validate_username(self, login_entry, login_text, event=None):

        is_valid_username = self.validate_username_strength(login_entry)

        self.format_username_label(
            login_text, ["Usuario valido", "Usuario inválido"], is_valid_username
        )

        if is_valid_username:
            return True

    def encrypt_password(self, password):
        """Hash da senha para gravar no banco (PBKDF2 com salt)."""
        return hash_password(password)

    @staticmethod
    def verify_password(password, stored):
        """Confere a senha digitada contra o hash gravado."""
        return verify_password(password, stored)
