from os import environ
from dotenv import load_dotenv
import ifaddr

# Only needed for developing, on production Docker .env file is used
load_dotenv()


class Config:
    """Set configuration vars from .env file."""
    CONSUL_HOST = environ.get("CONSUL_HOST", "192.168.7.201")
    CONSUL_PORT = environ.get("CONSUL_PORT", 8500)
    CONSUL_DNS_PORT = environ.get("CONSUL_DNS_PORT", 8600)
    PORT = int(environ.get("PORT", '80'))
    SERVICE_NAME = environ.get("SERVICE_NAME", "payments")
    SERVICE_ID = environ.get("SERVICE_ID", "payments1")
    IP = None

    __instance = None

    @staticmethod
    def get_instance():
        if Config.__instance is None:
            Config()
        return Config.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Config.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.get_ip()
            Config.__instance = self

    def get_ip(self):
        ip = Config.get_adapter_ip("eth0")  # this is the default interface in docker
        if ip is None:
            ip = "127.0.0.1"
        self.IP = ip

    @staticmethod
    def get_adapter_ip(nice_name):
        adapters = ifaddr.get_adapters()

        for adapter in adapters:
            if adapter.nice_name == nice_name and len(adapter.ips) > 0:
                return adapter.ips[0].ip

        return None
