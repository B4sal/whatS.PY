# ============================================================================
# WhatSPY - WhatsApp Number Intelligence Tool
# Desarrollado por: B4sal
# Descripción: Herramienta para consultar información de números de WhatsApp
# ============================================================================

import os
import re
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# Dependencias externas
import requests
from dotenv import load_dotenv
from colorama import Fore, Style, init, Back

# ============================================================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================================================

# Inicializar Colorama para compatibilidad con Windows
init(autoreset=True)

# Constantes de configuración
API_TIMEOUT: int = 30
LOG_FILE: str = 'whatSPY.log'
MAX_LOG_LINES: int = 20
MIN_PHONE_LENGTH: int = 10
MAX_PHONE_LENGTH: int = 15

# Configurar sistema de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WhatSPY:
    """
    WhatSPY - WhatsApp Number Intelligence Tool
    
    Esta clase proporciona funcionalidades completas para consultar información
    detallada de números de WhatsApp utilizando la API de RapidAPI.
    
    Características principales:
    - ✅ Validación automática de números telefónicos
    - ✅ Consultas a la API de WhatsApp Data
    - ✅ Formato JSON colorizado para mejor legibilidad
    - ✅ Sistema de logging completo
    - ✅ Exportación automática de resultados
    - ✅ Interfaz de usuario interactiva y colorida
    - ✅ Manejo robusto de errores de red
    
    Autor: B4sal
    Versión: 2.0
    """
    
    def __init__(self) -> None:
        """
        Inicializar la clase WhatSPY.
        
        Carga las variables de entorno y prepara la configuración necesaria
        para realizar consultas a la API de WhatsApp Data.
        
        Raises:
            SystemExit: Si no se encuentran las variables de entorno requeridas.
        """
        self.load_environment()
        
    def load_environment(self) -> None:
        """
        Cargar las variables de entorno desde el archivo .env.
        
        Busca y carga el archivo .env que debe contener:
        - RAPIDAPI_KEY: Clave de la API de RapidAPI
        - RAPIDAPI_HOST: Host de la API de WhatsApp Data
        
        Raises:
            SystemExit: Si las variables requeridas no están definidas.
        """
        try:
            load_dotenv()
            self.api_key = os.getenv('RAPIDAPI_KEY')
            self.api_host = os.getenv('RAPIDAPI_HOST')
            
            if not self.api_key or not self.api_host:
                raise ValueError(
                    "❌ Las variables de entorno RAPIDAPI_KEY y RAPIDAPI_HOST son requeridas."
                )
                
            logger.info("✅ Variables de entorno cargadas correctamente.")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error cargando variables de entorno: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Asegúrate de tener un archivo .env con:{Style.RESET_ALL}")
            print(f"   {Fore.CYAN}RAPIDAPI_KEY=tu_clave_aqui{Style.RESET_ALL}")
            print(f"   {Fore.CYAN}RAPIDAPI_HOST=whatsapp-data.p.rapidapi.com{Style.RESET_ALL}")
            sys.exit(1)
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validar formato del número de teléfono según estándares internacionales.
        
        Verifica que el número:
        - Contenga solo dígitos (después de limpiar formato)
        - Tenga longitud entre 10 y 15 dígitos
        - Cumpla con los estándares internacionales E.164
        
        Args:
            phone_number (str): Número de teléfono a validar
            
        Returns:
            bool: True si el formato es válido, False en caso contrario
            
        Examples:
            >>> whatspy = WhatSPY()
            >>> whatspy.validate_phone_number("+52 55 1234 5678")
            True
            >>> whatspy.validate_phone_number("123")
            False
        """
        if not phone_number or not isinstance(phone_number, str):
            return False
            
        # Remover espacios y caracteres especiales
        cleaned_number = re.sub(r'[\s\-\(\)\+]', '', phone_number)
        
        # Verificar que contenga solo dígitos
        if not cleaned_number.isdigit():
            return False
            
        # Verificar longitud según estándares internacionales E.164
        if len(cleaned_number) < MIN_PHONE_LENGTH or len(cleaned_number) > MAX_PHONE_LENGTH:
            return False
            
        return True
    
    def format_phone_number(self, phone_number: str) -> str:
        """
        Formatear número de teléfono removiendo caracteres especiales.
        
        Args:
            phone_number (str): Número de teléfono original
            
        Returns:
            str: Número formateado
        """
        return re.sub(r'[\s\-\(\)\+]', '', phone_number)
    
    def print_colored_json(self, data: Any, level: int = 0) -> None:
        """
        Imprimir JSON con formato y colores.
        
        Args:
            data: Datos a imprimir
            level (int): Nivel de indentación
        """
        indent = "    " * level
        
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"{indent}{Fore.CYAN}{key}{Style.RESET_ALL}: ", end="")
                if isinstance(value, (dict, list)):
                    print()
                    self.print_colored_json(value, level + 1)
                else:
                    self.print_colored_json(value, 0)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                print(f"{indent}{Fore.MAGENTA}[{i}]{Style.RESET_ALL}")
                self.print_colored_json(item, level + 1)
        else:
            color = Fore.GREEN if isinstance(data, bool) else Fore.YELLOW
            print(f"{color}{data}{Style.RESET_ALL}")
    
    def save_result_to_file(self, data: Dict[str, Any], phone_number: str) -> None:
        """
        Guardar resultado en archivo.
        
        Args:
            data: Datos a guardar
            phone_number: Número de teléfono consultado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"whatsapp_data_{phone_number}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"{Fore.GREEN}Resultado guardado en: {filename}{Style.RESET_ALL}")
            logger.info(f"Resultado guardado en archivo: {filename}")
        except Exception as e:
            print(f"{Fore.RED}Error al guardar archivo: {e}{Style.RESET_ALL}")
            logger.error(f"Error al guardar archivo: {e}")
    
    def query_whatsapp_number(self, phone_number: str, save_to_file: bool = False) -> Optional[Dict[str, Any]]:
        """
        Consultar información detallada de un número de WhatsApp.
        
        Realiza una consulta a la API de WhatsApp Data para obtener información
        sobre el número proporcionado. Maneja errores de red y API de forma robusta.
        
        Args:
            phone_number (str): Número de teléfono a consultar (con código de país)
            save_to_file (bool): Si guardar el resultado en archivo JSON
            
        Returns:
            Optional[Dict[str, Any]]: Información del número o None si hay error
            
        Raises:
            None: Todos los errores se manejan internamente y se registran
        """
        # Formatear y validar número
        formatted_number = self.format_phone_number(phone_number)
        
        # Preparar la consulta
        url = f"https://{self.api_host}/number/{formatted_number}"
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host,
            "User-Agent": "WhatSPY/2.0 (https://github.com/B4sal/whatS.PY)"
        }
        
        # Mostrar información de la consulta
        print(f"\n{Fore.CYAN}{'═' * 60}")
        print(f"🔍 {Fore.WHITE}CONSULTANDO NÚMERO: {Fore.YELLOW}{phone_number}")
        print(f"🌐 {Fore.WHITE}ENDPOINT: {Fore.BLUE}{url}")
        print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}")
        
        try:
            # Realizar solicitud con timeout
            print(f"{Fore.YELLOW}⏳ Realizando consulta a la API...{Style.RESET_ALL}")
            response = requests.get(url, headers=headers, timeout=API_TIMEOUT)
            
            # Log del estado de la respuesta
            logger.info(f"📡 Respuesta HTTP: {response.status_code} para {phone_number}")
            
            # Verificar status code
            response.raise_for_status()
            
            # Procesar respuesta JSON
            data = response.json()
            
            # Mostrar resultado exitoso
            print(f"\n{Fore.GREEN}{'🎉' * 20}")
            print(f"✅ {Fore.WHITE}CONSULTA EXITOSA PARA: {Fore.CYAN}{phone_number}")
            print(f"{Fore.GREEN}{'🎉' * 20}{Style.RESET_ALL}\n")
            
            # Mostrar datos formateados
            self.print_colored_json(data)
            
            # Guardar en archivo si se solicita
            if save_to_file:
                self.save_result_to_file(data, formatted_number)
            
            logger.info(f"✅ Consulta exitosa completada para: {phone_number}")
            return data
            
        except requests.exceptions.HTTPError as http_err:
            status_code = response.status_code if 'response' in locals() else 'Unknown'
            self._handle_http_error(http_err, status_code, phone_number, response if 'response' in locals() else None)
            
        except requests.exceptions.Timeout:
            error_msg = f"⏰ Timeout: La consulta para {phone_number} tardó más de {API_TIMEOUT} segundos"
            print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
            logger.error(error_msg)
            
        except requests.exceptions.ConnectionError:
            error_msg = f"🌐 Error de conexión al consultar {phone_number}. Verifica tu conexión a internet"
            print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
            logger.error(error_msg)
            
        except json.JSONDecodeError:
            error_msg = f"📄 La respuesta de la API no es un JSON válido para {phone_number}"
            print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
            logger.error(error_msg)
            
        except Exception as err:
            error_msg = f"💥 Error inesperado al consultar {phone_number}: {err}"
            print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
            logger.error(error_msg)
        
        return None
    
    def _handle_http_error(self, http_err: requests.exceptions.HTTPError, status_code: int, 
                          phone_number: str, response: Optional[requests.Response]) -> None:
        """
        Manejar errores HTTP de forma detallada.
        
        Args:
            http_err: Error HTTP ocurrido
            status_code: Código de estado de la respuesta
            phone_number: Número consultado
            response: Respuesta HTTP (opcional)
        """
        error_msg = f"🔴 Error HTTP {status_code} al consultar {phone_number}: {http_err}"
        print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
        logger.error(error_msg)
        
        # Mostrar detalles del error si están disponibles
        if response:
            try:
                error_detail = response.json()
                print(f"\n{Fore.YELLOW}📋 Detalles del error:{Style.RESET_ALL}")
                self.print_colored_json(error_detail)
            except (json.JSONDecodeError, ValueError):
                if response.text:
                    print(f"{Fore.YELLOW}📋 Respuesta del servidor: {response.text[:200]}...{Style.RESET_ALL}")
    
    def show_banner(self) -> None:
        """Mostrar banner de la aplicación con estilo mejorado."""
        banner = f"""
{Fore.CYAN}{Style.BRIGHT}
██╗    ██╗██╗  ██╗ █████╗ ████████╗███████╗██████╗ ██╗   ██╗
██║    ██║██║  ██║██╔══██╗╚══██╔══╝██╔════╝██╔══██╗╚██╗ ██╔╝
██║ █╗ ██║███████║███████║   ██║   ███████╗██████╔╝ ╚████╔╝ 
██║███╗██║██╔══██║██╔══██║   ██║   ╚════██║██╔═══╝   ╚██╔╝  
╚███╔███╔╝██║  ██║██║  ██║   ██║   ███████║██║        ██║   
 ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝        ╚═╝   

{Fore.YELLOW}WhatsApp Number Intelligence Tool{Style.RESET_ALL}

{Fore.WHITE}Desarrollado por: {Fore.RED}B4sal{Style.RESET_ALL}

{Fore.CYAN}Funciones principales:{Style.RESET_ALL}
{Fore.CYAN}• Consulta información detallada de números WhatsApp{Style.RESET_ALL}
{Fore.CYAN}• Exporta resultados en formato JSON{Style.RESET_ALL}
{Fore.CYAN}• Sistema de logs completo{Style.RESET_ALL}
{Fore.CYAN}• Interfaz colorida y fácil de usar{Style.RESET_ALL}
        """
        print(banner)
    
    def show_menu(self) -> int:
        """
        Mostrar menú principal con diseño mejorado.
        
        Returns:
            int: Opción seleccionada por el usuario
        """
        print(f"\n{Fore.CYAN}{Style.BRIGHT}MENÚ PRINCIPAL{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}1.{Fore.WHITE} Consultar número de WhatsApp")
        print(f"{Fore.YELLOW}2.{Fore.WHITE} Consultar y guardar resultado") 
        print(f"{Fore.YELLOW}3.{Fore.WHITE} Ver logs del sistema")
        print(f"{Fore.YELLOW}4.{Fore.WHITE} Limpiar pantalla")
        print(f"{Fore.YELLOW}5.{Fore.WHITE} Ver ayuda y documentación")
        print()
        print(f"{Fore.RED}0.{Fore.WHITE} Salir del programa")
        print(f"{Style.RESET_ALL}")
        
        try:
            choice = int(input(f"{Fore.GREEN}Selecciona una opción: {Style.RESET_ALL}"))
            return choice
        except ValueError:
            print(f"{Fore.RED}Por favor ingresa un número válido.{Style.RESET_ALL}")
            return -1
    
    def show_help(self) -> None:
        """Mostrar ayuda del programa con diseño mejorado."""
        help_text = f"""
{Fore.CYAN}{Style.BRIGHT}GUÍA DE USO - WHATSPY{Style.RESET_ALL}

{Fore.YELLOW}FORMATO DE NÚMEROS VÁLIDOS:{Style.RESET_ALL}

  • {Fore.GREEN}Con código de país:{Fore.WHITE} +52 55 1234 5678, +1 555 123 4567
  • {Fore.GREEN}Sin espacios:{Fore.WHITE} 5215512345678
  • {Fore.GREEN}Con paréntesis:{Fore.WHITE} (555) 123-4567

{Fore.YELLOW}CONFIGURACIÓN REQUERIDA:{Style.RESET_ALL}

  1. Crear archivo {Fore.MAGENTA}.env{Style.RESET_ALL} en el directorio del proyecto
  2. Añadir las siguientes variables:
     {Fore.GREEN}RAPIDAPI_KEY={Fore.WHITE}tu_clave_api_aqui
     {Fore.GREEN}RAPIDAPI_HOST={Fore.WHITE}whatsapp-data.p.rapidapi.com

{Fore.YELLOW}ARCHIVOS GENERADOS:{Style.RESET_ALL}

  • {Fore.MAGENTA}whatSPY.log{Fore.WHITE} - Registro detallado de actividades
  • {Fore.MAGENTA}whatsapp_data_*.json{Fore.WHITE} - Resultados de consultas

{Fore.YELLOW}FUNCIONALIDADES PRINCIPALES:{Style.RESET_ALL}

  ✅ Validación automática de números de teléfono
  ✅ Formato JSON con colores para mejor lectura
  ✅ Guardado automático de resultados
  ✅ Sistema de logging completo
  ✅ Manejo robusto de errores de red
  ✅ Interfaz colorida y fácil de usar

{Fore.YELLOW}CONSEJOS:{Style.RESET_ALL}

  • Siempre incluye el código de país en el número
  • Revisa los logs si encuentras errores
  • Los resultados se guardan automáticamente con timestamp
{Style.RESET_ALL}
        """
        print(help_text)
    
    def clear_screen(self) -> None:
        """Limpiar pantalla."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_logs(self) -> None:
        """Mostrar las últimas líneas del log con formato mejorado."""
        try:
            # Intentar abrir el archivo con diferentes codificaciones
            try:
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                try:
                    with open(LOG_FILE, 'r', encoding='latin-1') as f:
                        lines = f.readlines()
                except Exception:
                    with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        
            # Obtener las últimas líneas
            recent_lines = lines[-MAX_LOG_LINES:] if len(lines) > MAX_LOG_LINES else lines

            print(f"\n{Fore.CYAN}╔{'═' * 70}╗")
            print(f"║{' ' * 25}📋 REGISTRO DE ACTIVIDADES 📋{' ' * 25}║")
            print(f"╠{'═' * 70}╣")
            print(f"║ {Fore.YELLOW}📊 Mostrando las últimas {len(recent_lines)} entradas:{' ' * 33}{Fore.CYAN}║")
            print(f"╚{'═' * 70}╝{Style.RESET_ALL}\n")

            for i, line in enumerate(recent_lines, 1):
                line = line.strip()
                if 'ERROR' in line or 'CRITICAL' in line:
                    color = Fore.RED
                    icon = "❌"
                elif 'WARNING' in line:
                    color = Fore.YELLOW  
                    icon = "⚠️"
                elif 'INFO' in line:
                    color = Fore.GREEN
                    icon = "ℹ️"
                else:
                    color = Fore.WHITE
                    icon = "📝"
                
                print(f"{Fore.CYAN}[{i:2d}]{color} {icon} {line}{Style.RESET_ALL}")

            print(f"\n{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")

        except FileNotFoundError:
            print(f"\n{Fore.YELLOW}╔{'═' * 50}╗")
            print(f"║{' ' * 16}⚠️ AVISO ⚠️{' ' * 17}║")
            print(f"╠{'═' * 50}╣")
            print(f"║ No se encontró archivo de log.{' ' * 17}║")
            print(f"║ Ejecuta una consulta para generar logs.{' ' * 9}║")
            print(f"╚{'═' * 50}╝{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error al leer logs: {e}{Style.RESET_ALL}")
    
    def run(self) -> None:
        """Ejecutar el programa principal."""
        self.clear_screen()
        self.show_banner()
        
        while True:
            choice = self.show_menu()
            
            if choice == 1:
                # Consultar número
                phone = input(f"\n{Fore.GREEN}Introduce el número de teléfono (con código de país): {Style.RESET_ALL}")
                if self.validate_phone_number(phone):
                    self.query_whatsapp_number(phone)
                else:
                    print(f"{Fore.RED}Número de teléfono inválido. Verifica el formato.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Presiona Enter para continuar...{Style.RESET_ALL}")
                
            elif choice == 2:
                # Consultar y guardar
                phone = input(f"\n{Fore.GREEN}Introduce el número de teléfono (con código de país): {Style.RESET_ALL}")
                if self.validate_phone_number(phone):
                    self.query_whatsapp_number(phone, save_to_file=True)
                else:
                    print(f"{Fore.RED}Número de teléfono inválido. Verifica el formato.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Presiona Enter para continuar...{Style.RESET_ALL}")
                
            elif choice == 3:
                # Ver logs
                self.show_logs()
                input(f"\n{Fore.CYAN}Presiona Enter para continuar...{Style.RESET_ALL}")
                
            elif choice == 4:
                # Limpiar pantalla
                self.clear_screen()
                self.show_banner()
                
            elif choice == 5:
                # Ayuda
                self.show_help()
                input(f"\n{Fore.CYAN}Presiona Enter para continuar...{Style.RESET_ALL}")
                
            elif choice == 0:
                # Salir
                print(f"\n{Fore.GREEN}{'=' * 50}")
                print(f"🎉 ¡Gracias por usar WhatSPY! 🎉")
                print(f"{'=' * 50}")
                print(f"{Fore.CYAN}📧 Desarrollado por: {Fore.RED}B4sal")
                print(f"{Fore.CYAN}🌟 GitHub: {Fore.BLUE}https://github.com/B4sal/whatS.PY")
                print(f"{Fore.YELLOW}⭐ ¡No olvides darle una estrella al proyecto!")
                print(f"{'=' * 50}{Style.RESET_ALL}")
                logger.info("Programa terminado por el usuario")
                break
                
            else:
                if choice != -1:
                    print(f"{Fore.RED}Opción inválida. Por favor selecciona una opción del menú.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Presiona Enter para continuar...{Style.RESET_ALL}")


def main():
    """Función principal."""
    try:
        app = WhatSPY()
        app.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Programa interrumpido por el usuario.{Style.RESET_ALL}")
        logger.info("Programa interrumpido por el usuario (Ctrl+C)")
    except Exception as e:
        print(f"\n{Fore.RED}Error crítico: {e}{Style.RESET_ALL}")
        logger.critical(f"Error crítico: {e}")


if __name__ == "__main__":
    main()
