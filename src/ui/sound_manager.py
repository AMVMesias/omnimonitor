"""
Sistema de Sonidos para OmniMonitor
Reproduce sonidos de notificación para alertas
"""
import os
import sys
import threading
from typing import Optional


class SoundManager:
    """
    Gestor de sonidos para notificaciones
    Soporta múltiples backends: playsound, pygame, system beep
    """
    
    _enabled: bool = True
    _backend: Optional[str] = None
    _initialized: bool = False
    
    # Rutas de sonidos (relativos al directorio del proyecto)
    SOUNDS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'sounds')
    
    @classmethod
    def initialize(cls):
        """Inicializar el sistema de sonidos y detectar backend disponible"""
        if cls._initialized:
            return
        
        # Crear directorio de sonidos si no existe
        if not os.path.exists(cls.SOUNDS_DIR):
            os.makedirs(cls.SOUNDS_DIR)
        
        # Detectar backend disponible
        cls._backend = cls._detect_backend()
        cls._initialized = True
        print(f"SoundManager inicializado con backend: {cls._backend}")
    
    @classmethod
    def _detect_backend(cls) -> Optional[str]:
        """Detectar qué biblioteca de sonido está disponible"""
        
        # Intentar con pygame (más confiable)
        try:
            import pygame
            pygame.mixer.init()
            return "pygame"
        except:
            pass
        
        # Intentar con playsound
        try:
            from playsound import playsound
            return "playsound"
        except:
            pass
        
        # En Linux, verificar si hay paplay (PulseAudio)
        if sys.platform.startswith('linux'):
            try:
                import subprocess
                result = subprocess.run(['which', 'paplay'], capture_output=True)
                if result.returncode == 0:
                    return "paplay"
            except:
                pass
            
            # Verificar aplay (ALSA)
            try:
                import subprocess
                result = subprocess.run(['which', 'aplay'], capture_output=True)
                if result.returncode == 0:
                    return "aplay"
            except:
                pass
        
        # Fallback: beep del sistema
        return "beep"
    
    @classmethod
    def set_enabled(cls, enabled: bool):
        """Habilitar o deshabilitar sonidos"""
        cls._enabled = enabled
    
    @classmethod
    def is_enabled(cls) -> bool:
        """Verificar si los sonidos están habilitados"""
        return cls._enabled
    
    @classmethod
    def _play_with_pygame(cls, sound_file: str):
        """Reproducir sonido con pygame"""
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            sound = pygame.mixer.Sound(sound_file)
            sound.play()
        except Exception as e:
            print(f"Error reproduciendo sonido con pygame: {e}")
    
    @classmethod
    def _play_with_playsound(cls, sound_file: str):
        """Reproducir sonido con playsound"""
        try:
            from playsound import playsound
            playsound(sound_file, block=False)
        except Exception as e:
            print(f"Error reproduciendo sonido con playsound: {e}")
    
    @classmethod
    def _play_with_paplay(cls, sound_file: str):
        """Reproducir sonido con paplay (PulseAudio) a volumen alto"""
        try:
            import subprocess
            # Volumen 65536 = 100%, usar 80000 para más fuerte
            subprocess.Popen(['paplay', '--volume=80000', sound_file], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Error reproduciendo sonido con paplay: {e}")
    
    @classmethod
    def _play_with_aplay(cls, sound_file: str):
        """Reproducir sonido con aplay (ALSA)"""
        try:
            import subprocess
            subprocess.Popen(['aplay', '-q', sound_file], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Error reproduciendo sonido con aplay: {e}")
    
    @classmethod
    def _play_system_beep(cls):
        """Reproducir beep del sistema como fallback"""
        try:
            if sys.platform.startswith('linux'):
                import subprocess
                # Intentar con speaker-test para un beep corto
                subprocess.Popen(['paplay', '/usr/share/sounds/freedesktop/stereo/message.oga'],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            elif sys.platform == 'darwin':  # macOS
                os.system('afplay /System/Library/Sounds/Ping.aiff &')
            else:  # Windows
                import winsound
                winsound.MessageBeep()
        except Exception as e:
            # Último recurso: print bell character
            print('\a', end='', flush=True)
    
    @classmethod
    def _play_sound_file(cls, sound_file: str):
        """Reproducir archivo de sonido usando el backend disponible"""
        if not os.path.exists(sound_file):
            cls._play_system_beep()
            return
        
        if cls._backend == "pygame":
            cls._play_with_pygame(sound_file)
        elif cls._backend == "playsound":
            cls._play_with_playsound(sound_file)
        elif cls._backend == "paplay":
            cls._play_with_paplay(sound_file)
        elif cls._backend == "aplay":
            cls._play_with_aplay(sound_file)
        else:
            cls._play_system_beep()
    
    @classmethod
    def play_notification(cls, sound_type: str = "alert"):
        """
        Reproducir sonido de notificación
        
        Args:
            sound_type: Tipo de sonido ("alert", "success", "error", "warning", "info")
        """
        if not cls._enabled:
            return
        
        if not cls._initialized:
            cls.initialize()
        
        # Ejecutar en thread separado para no bloquear UI
        def play_async():
            try:
                # Buscar archivo de sonido
                sound_files = {
                    "alert": ["alert.wav", "alert.ogg", "alert.mp3"],
                    "success": ["success.wav", "success.ogg", "success.mp3"],
                    "error": ["error.wav", "error.ogg", "error.mp3"],
                    "warning": ["warning.wav", "warning.ogg", "warning.mp3"],
                    "info": ["info.wav", "info.ogg", "info.mp3"],
                }
                
                # Buscar archivo existente
                files_to_try = sound_files.get(sound_type, sound_files["alert"])
                sound_file = None
                
                for filename in files_to_try:
                    filepath = os.path.join(cls.SOUNDS_DIR, filename)
                    if os.path.exists(filepath):
                        sound_file = filepath
                        break
                
                # Si no hay archivo personalizado, intentar sonidos del sistema
                if not sound_file:
                    system_sounds = [
                        "/usr/share/sounds/freedesktop/stereo/message.oga",
                        "/usr/share/sounds/freedesktop/stereo/complete.oga",
                        "/usr/share/sounds/freedesktop/stereo/bell.oga",
                        "/usr/share/sounds/gnome/default/alerts/drip.ogg",
                        "/usr/share/sounds/ubuntu/notifications/Mallet.ogg",
                    ]
                    
                    for sys_sound in system_sounds:
                        if os.path.exists(sys_sound):
                            sound_file = sys_sound
                            break
                
                if sound_file:
                    cls._play_sound_file(sound_file)
                else:
                    cls._play_system_beep()
                    
            except Exception as e:
                print(f"Error en play_notification: {e}")
        
        thread = threading.Thread(target=play_async, daemon=True)
        thread.start()
    
    @classmethod
    def play_alert(cls):
        """Reproducir sonido de alerta"""
        cls.play_notification("alert")
    
    @classmethod
    def play_success(cls):
        """Reproducir sonido de éxito"""
        cls.play_notification("success")
    
    @classmethod
    def play_error(cls):
        """Reproducir sonido de error"""
        cls.play_notification("error")
    
    @classmethod
    def play_warning(cls):
        """Reproducir sonido de advertencia"""
        cls.play_notification("warning")
    
    @classmethod
    def play_info(cls):
        """Reproducir sonido informativo"""
        cls.play_notification("info")


# Inicializar al importar
SoundManager.initialize()
