# run.py
import sys
import io

# Configura o sistema para usar UTF-8 como padrão
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Importa e executa o pgzero
from pgzero.__main__ import main
main()
