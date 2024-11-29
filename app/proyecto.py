import flet as ft
import cv2
import h5py
import numpy as np
import os

def main(page: ft.Page):
    output_folder = ft.Text(value="No folder selected", size=12, italic=True)

    def process_video(file_path, output_dir):
        try:
            status.value += f"Procesando el video: {file_path}\n"
            page.update()
            
            # Leer el video con OpenCV
            cap = cv2.VideoCapture(file_path)
            frames = []

            if not cap.isOpened():
                status.value += f"No se pudo abrir el video: {file_path}\n"
                page.update()
                return

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                # Reducir el tamaño del frame para optimización
                resized_frame = cv2.resize(frame, (128, 128))
                frames.append(resized_frame)

            cap.release()
            frames_array = np.array(frames)

            if frames_array.size == 0:
                status.value += f"El video no contiene frames procesables: {file_path}\n"
                page.update()
                return

            # Guardar en un archivo .h5
            video_name = os.path.basename(file_path)
            h5_file = os.path.join(output_dir, os.path.splitext(video_name)[0] + ".h5")
            with h5py.File(h5_file, "w") as hf:
                hf.create_dataset("video_frames", data=frames_array)
            
            status.value += f"Procesado y guardado: {h5_file}\n"
            page.update()
        except Exception as e:
            status.value += f"Error procesando {file_path}: {e}\n"
            page.update()

    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files and output_folder.value != "No folder selected":
            status.value = "Procesando videos...\n"
            page.update()
            for file in e.files:
                process_video(file.path, output_folder.value)
        else:
            status.value = "Por favor selecciona una carpeta de destino primero."
            page.update()

    def select_folder_result(e: ft.FilePickerResultEvent):
        if e.path:
            output_folder.value = e.path
            page.update()

    # Configurar el FilePicker para archivos y carpetas
    file_picker = ft.FilePicker(on_result=pick_files_result)
    folder_picker = ft.FilePicker(on_result=select_folder_result)
    page.overlay.append(file_picker)
    page.overlay.append(folder_picker)

    # Botones y textos de la UI
    pick_files_button = ft.ElevatedButton(
        "Seleccionar videos",
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=True, allowed_extensions=["mp4", "avi", "mov","m4v","m4a"]
        )
    )
    select_folder_button = ft.ElevatedButton(
        "Seleccionar carpeta de destino",
        on_click=lambda _: folder_picker.get_directory_path()
    )
    status = ft.Text(value="")

    # Agregar elementos a la página
    page.add(
        select_folder_button,
        output_folder,
        pick_files_button,
        status
    )

# Ejecutar la app
ft.app(target=main)

