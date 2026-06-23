from typing import Callable, Union

EncryptFn = Callable[[Union[str, int]], str]
DecryptFn = Callable[[str], str]