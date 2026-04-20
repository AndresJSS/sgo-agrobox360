// 1. Calculadora de rendimiento de cosecha

document.addEventListener('DOMContentLoaded', function() {
    
    const inputsCosecha = document.querySelectorAll('.input-cosecha');

    inputsCosecha.forEach(input => {
        input.addEventListener('input', function() {
            
            const id = this.getAttribute('data-id');
            const totalPlantas = parseInt(this.getAttribute('data-total'));
            const inputCosechadas = this.value;
            
            const cajaRendimiento = document.getElementById('caja_rendimiento_' + id);
            const textoRendimiento = document.getElementById('texto_rendimiento_' + id);

            if (inputCosechadas !== "" && !isNaN(inputCosechadas) && inputCosechadas >= 0) {
                let cosechadas = parseInt(inputCosechadas);
                let porcentaje = ((cosechadas / totalPlantas) * 100).toFixed(1);

                textoRendimiento.innerText = porcentaje + "%";
                cajaRendimiento.style.display = 'block';

                // 1. Limpiamos todas las clases de color posibles de la tarjeta
                cajaRendimiento.classList.remove('bg-iica-red', 'bg-warning', 'bg-iica-green', 'text-white', 'text-dark', 'border-0');
                
                // 2. Pintamos la tarjeta completa según el porcentaje
                if (porcentaje < 60) {
                    // Tarjeta ROJA (Letras blancas)
                    cajaRendimiento.classList.add('bg-iica-red', 'text-white', 'border-0'); 
                } else if (porcentaje <= 75) {
                    // Tarjeta AMARILLA (Letras oscuras para que se lea bien)
                    cajaRendimiento.classList.add('bg-warning', 'text-dark', 'border-0');  
                } else {
                    // Tarjeta VERDE (Letras blancas)
                    cajaRendimiento.classList.add('bg-iica-green', 'text-white', 'border-0'); 
                }
            } else {
                cajaRendimiento.style.display = 'none';
            }
        });
    });
});


// 2. Tablas dinámicas

$(document).ready(function() {
    $('.tabla-dinamica').DataTable({
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json'
        },
        pageLength: 10,
        order: [], 
        
        //Generador automático de filtros por columna
        initComplete: function () {
            console.log("Iniciando filtros V3 (Blindados)");
            
            // Iteración en todas las columnas de la tabla
            this.api().columns().every(function () {
                var column = this;
                var colIdx = column.index();
                var pieColumna = $(column.footer());
                
                // Si la tabla no tiene <tfoot>, la ignoramos
                if (!pieColumna || !pieColumna.length) return;

                var titulo = pieColumna.text().trim();
                
                // Si el <th> en el HTML está vacío, detenemos la creación del filtro
                if (titulo === "") return;

                // Si hay texto, procedemos a crear el select normalmente
                pieColumna.empty();
                var select = $('<select class="form-select form-select-sm"><option value="">Todo ' + titulo + '</option></select>')
                    .appendTo(pieColumna)
                    .on('change', function () {
                        var val = $.fn.dataTable.util.escapeRegex($(this).val());
                        
                        // Si es la columna 0 (Fecha), busca "Empieza con" (^val)
                        if (colIdx === 0 && val) {
                            column.search('^' + val, true, false).draw();
                        } else {
                            // Para las demás, busca coincidencia exacta (^val$)
                            column.search(val ? '^' + val + '$' : '', true, false).draw();
                        }
                    });

                var opcionesUnicas = [];
                
                column.data().each(function (d) {
                    // Validamos que 'd' exista para evitar errores si hay celdas vacías
                    if (d) {
                        var textoLimpio = $('<div>').html(d).text().trim();
                        if (textoLimpio !== "") {
                            // Cortar la hora solo en la primera columna
                            if (colIdx === 0) {
                                textoLimpio = textoLimpio.split(' ')[0];
                            }
                            // Agregar a la lista si no existe aún
                            if (opcionesUnicas.indexOf(textoLimpio) === -1) {
                                opcionesUnicas.push(textoLimpio);
                            }
                        }
                    }
                });

                // Ordenar alfabéticamente/cronológicamente y agregar al HTML
                opcionesUnicas.sort();
                $.each(opcionesUnicas, function(index, val) {
                    select.append('<option value="' + val + '">' + val + '</option>');
                });
            });
        }
    });
});