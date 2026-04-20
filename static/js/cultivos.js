document.addEventListener('DOMContentLoaded', function() {
    const selectUbicacion = document.getElementById('select-ubicacion');
    const labelCantidad = document.getElementById('label-cantidad');

    if(selectUbicacion && labelCantidad) {
        selectUbicacion.addEventListener('change', function() {
            const valorSeleccionado = this.value;

            if(valorSeleccionado.includes('PLA')) {
                labelCantidad.textContent = 'No.Bandejas';
            } else {
                labelCantidad.textContent = 'No.Plantas';
            }
        });
    }
});