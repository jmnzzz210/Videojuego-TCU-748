# Proyecto: Ecos en la Estación
# Autores: Marvin Coto Jiménez y Brandon Jiménez Campos
# TCU-748 Tecnoinclusión UCR

.PHONY: help install run clean

help:
	@echo "======================================================"
	@echo "  ECOS EN LA ESTACIÓN - COMANDOS DE AUTOMATIZACIÓN"
	@echo "======================================================"
	@echo "  make install   - Instala las dependencias (requirements.txt)"
	@echo "  make run       - Ejecuta el videojuego"
	@echo "  make clean     - Limpia archivos temporales y caché de Python"
	@echo "======================================================"

install:
	pip install -r requirements.txt

run:
	python3 main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

