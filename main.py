# main.py
import sys
import os

# Truco para que Python encuentre tus carpetas src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importaciones desde TUS carpetas
from src.io.hgt_loader import HGTLoader
from src.io.display import TerrainDisplay
from core.terrain_ops import TerrainOperations

def main():
    # 1. Configuración
    archivo = "data/SA17/S01W079.hgt" # Asegúrate de que este archivo exista en tu carpeta data/
    
    # 2. Instanciar el cargador
    loader = HGTLoader()
    
    print(f"Cargando archivo: {archivo}...")
    raw_map = loader.load_file(archivo)
    
    if raw_map is not None:
        # 3. Procesamiento (Usando core)
        print("Limpiando datos void...")
        clean_map = TerrainOperations.handle_voids(raw_map)
        
        # 4. Recorte de prueba (Ej. Cotopaxi suele estar por el centro aprox)
        print("Recortando zona de interés...")
        # Nota: Estas coordenadas son ejemplo, tendrás que buscar las exactas
        mini_map = TerrainOperations.crop_area(clean_map, 400, 400, 300, 300)
        
        # 5. Visualización (Usando io)
        print("Generando visualización...")
        TerrainDisplay.plot_terrain(mini_map, title="Vista Previa Proyecto Mapa 3D")

if __name__ == "__main__":
    main()