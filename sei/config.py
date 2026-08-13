"""Configuração do robô, lida do .env."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# O login do SEI-DF acontece no SIP, não no domínio do SEI. URL conforme gravada
# pelo codegen; infra_url=L3NlaS8= é "/sei/" em base64 (para onde o SIP redireciona).
URL_LOGIN_SIP = (
    "https://sip.df.gov.br/sip/login.php"
    "?sigla_orgao_sistema=GDF&sigla_sistema=SEI&infra_url=L3NlaS8="
)

CHAVES_OBRIGATORIAS = ("SEI_USUARIO", "SEI_SENHA", "SEI_Orgao", "SEI_SENHA_CREDENCIAL")


@dataclass(frozen=True)
class Config:
    url_login: str
    usuario: str
    senha: str
    orgao: str
    senha_credencial: str
    headless: bool
    limite: int | None
    abas: int

    @classmethod
    def carregar(cls) -> Config:
        load_dotenv()

        faltando = [c for c in CHAVES_OBRIGATORIAS if not os.getenv(c, "").strip()]
        if faltando:
            raise RuntimeError(f"Preencha no .env: {', '.join(faltando)}")

        # SEI_URL normalmente guarda só a base (https://sei.df.gov.br). Só a usamos
        # como URL de login se ela já apontar para a tela de login do SIP.
        url = os.getenv("SEI_URL", "").strip()
        limite = os.getenv("LIMITE", "").strip()

        return cls(
            url_login=url if "login.php" in url else URL_LOGIN_SIP,
            usuario=os.getenv("SEI_USUARIO", "").strip(),
            senha=os.getenv("SEI_SENHA", "").strip(),
            orgao=os.getenv("SEI_Orgao", "").strip(),
            senha_credencial=os.getenv("SEI_SENHA_CREDENCIAL", "").strip(),
            headless=os.getenv("HEADLESS", "false").strip().lower()
            in ("1", "true", "sim"),
            limite=int(limite) if limite.isdigit() else None,
            abas=max(1, int(os.getenv("ABAS", "4"))),
        )
