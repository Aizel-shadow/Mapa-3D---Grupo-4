import os
import sys
import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import rasterio
from rasterio.plot import show

# Configuración de rutas para encontrar src/core y src/io
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'src'))

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class EcuadorMapVisor(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Visor Topográfico de Ecuador Continental - Grupo 4")
        self.geometry("1300x850")

        # --- Mapeo de Regiones a Archivos Renderizados ---
        # Basado en las zonas definidas en build_all_zones.py
        self.regiones = {
            "Costa": ["A17_full.tif", "SA17_full.tif"],
            "Sierra": ["A17_full.tif", "SA17_full.tif", "A18_full.tif", "SA18_full.tif"],
            "Oriente": ["A18_full.tif", "SA18_full.tif", "SB17_full.tif", "SB18_full.tif"],
            "Todo el Ecuador": ["A17_full.tif", "A18_full.tif", "SA17_full.tif", "SA18_full.tif", "SB17_full.tif", "SB18_full.tif"]
        }

        self.setup_ui()

    def setup_ui(self):
        # Configuración de Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Panel Lateral (Menú) ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="MENÚ GEOGRÁFICO", font=("Arial", 22, "bold")).pack(pady=20)
        
        ctk.CTkLabel(self.sidebar, text="Visualizar por Región:", font=("Arial", 14)).pack(pady=(10, 5))
        
        for region in self.regiones.keys():
            ctk.CTkButton(self.sidebar, text=region, font=("Arial", 13),
                          command=lambda r=region: self.load_region(r)).pack(pady=8, padx=25, fill="x")

        # Información de ayuda
        help_text = "Use la lupa para Zoom\ny la mano para Pan."
        ctk.CTkLabel(self.sidebar, text=help_text, text_color="gray", font=("Arial", 11)).pack(side="bottom", pady=20)

        # --- Área de Visualización (Mapa) ---
        self.map_container = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.map_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # Preparar la figura de Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(10, 10), facecolor='#1a1a1a')
        self.ax.set_facecolor('#000000')
        self.ax.tick_params(colors='white', labelsize=9)
        self.ax.set_title("Seleccione una región en el menú lateral", color='white', pad=20)

        # Integrar Canvas en CustomTkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.map_container)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Herramientas de navegación (Zoom, Pan, Save)
        self.toolbar_frame = ctk.CTkFrame(self.map_container, height=40, fg_color="transparent")
        self.toolbar_frame.pack(side="bottom", fill="x")
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()

    def load_region(self, region_name):
        """Carga y procesa los archivos GeoTIFF renderizados para la región seleccionada."""
        self.ax.clear()
        self.ax.set_title(f"Procesando Región: {region_name}...", color='yellow')
        self.canvas.draw()

        output_path = os.path.join(BASE_DIR, "outputs", "dem")
        files_to_load = self.regiones[region_name]
        
        data_found = False
        
        try:
            for filename in files_to_load:
                file_full_path = os.path.join(output_path, filename)
                
                if os.path.exists(file_full_path):
                    with rasterio.open(file_full_path) as src:
                        # Leemos la banda de elevación
                        # Al ser archivos pesados, rasterio gestiona la lectura eficiente
                        elevation_data = src.read(1)
                        
                        # Definimos el extent (latitud/longitud) para posicionar el tile correctamente
                        # src.bounds provee: (left, bottom, right, top)
                        tile_extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
                        
                        # Renderizamos con el colormap 'terrain' definido en tu código original
                        img = self.ax.imshow(elevation_data, extent=tile_extent, 
                                            cmap='terrain', origin='upper')
                        data_found = True
                else:
                    print(f"[ADVERTENCIA] No se encontró el archivo renderizado: {filename}")

            if data_found:
                self.ax.set_title(f"Mapa de Elevación - {region_name}", color='white', fontsize=16)
                self.ax.set_xlabel("Longitud (Grados)", color='white')
                self.ax.set_ylabel("Latitud (Grados)", color='white')
                self.ax.grid(True, color='gray', linestyle='--', alpha=0.3)
                
                # Añadir barra de colores (solo una vez)
                if not hasattr(self, 'colorbar'):
                    self.colorbar = self.fig.colorbar(img, ax=self.ax, fraction=0.046, pad=0.04)
                    self.colorbar.set_label('Altura [m]', color='white')
                    self.colorbar.ax.yaxis.set_tick_params(color='white', labelcolor='white')
                
                self.canvas.draw()
            else:
                messagebox.showerror("Error de Datos", 
                                   "No se encontraron archivos renderizados en 'outputs/dem/'.\n"
                                   "Por favor, ejecute primero 'build_all_zones.py'.")

        except Exception as e:
            messagebox.showerror("Error", f"Fallo al cargar la visualización: {str(e)}")

if __name__ == "__main__":
    app = EcuadorMapVisor()
    app.mainloop()
    