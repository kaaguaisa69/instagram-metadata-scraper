import random
import time


def human_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> float:
    """
    Espera un tiempo aleatorio entre min_seconds y max_seconds
    para simular comportamiento humano.

    Retorna el número de segundos dormidos.
    """

    wait = random.uniform(min_seconds, max_seconds)
    time.sleep(wait)
    return wait
