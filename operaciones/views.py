from django.shortcuts import render, redirect, get_object_or_404
from .models import Cultivo, Tarea, Insumo, HistorialOperacion
from django.utils import timezone

def dashboard(request):
    # 1. Procesar formulario de creación de cultivo
    if request.method == 'POST' and 'nuevo_cultivo' in request.POST:
        nuevo_subsistema = request.POST.get('subsistema')
        fecha_ingreso = request.POST.get('fecha_siembra')
        cantidad_raw = request.POST.get('cantidad_bandejas')
        cantidad = int(cantidad_raw) if cantidad_raw else 1
        detalles_registro = request.POST.get('detalles')

        # Detectar automáticamete el sistema macro según el subsistema elegido
        if 'PLA' in nuevo_subsistema:
            sistema_macro = 'PLA'
        elif 'MAD' in nuevo_subsistema:
            sistema_macro = 'MAD'
        elif 'VER' in nuevo_subsistema:
            sistema_macro = 'VER'
        else:
            sistema_macro = 'PLA'  # Por seguridad
        
        # Al ingresar directo a maduración/vertical, la fecha de traspaso es hoy mismo
        fecha_traspaso = fecha_ingreso if sistema_macro != 'PLA' else None

        # Cultivo recién creado en variable "nuevo_cultivo"
        nuevo_cultivo = Cultivo.objects.create(
            nombre=request.POST.get('nombre'),
            variedad=request.POST.get('variedad'),
            fecha_siembra=fecha_ingreso,
            sistema_produccion=sistema_macro,
            subsistema=nuevo_subsistema,
            fecha_traspaso_real=fecha_traspaso,
            cantidad_bandejas=cantidad,
            estado='GER',
            detalles=detalles_registro,
        )

        # Guardar el nuevo registro para el historial
        HistorialOperacion.objects.create(
            tipo_accion='REGISTRO',
            lote_id_afectado=nuevo_cultivo.lote_id,
            cultivo_nombre=f"{nuevo_cultivo.nombre} ({nuevo_cultivo.variedad})",
            fecha_siembra_registrada=nuevo_cultivo.fecha_siembra,
            subsistema_registrado=nuevo_cultivo.subsistema,
            cantidad=nuevo_cultivo.cantidad_bandejas,
            detalles=detalles_registro,
        )
        return redirect('/?tab=cultivos')
    
    # Leer la URL para ver si hay alguna instrucción de abrir pestaña
    tab_activa = request.GET.get('tab', '')

    # Ocultar cosechados
    cultivos_activos = Cultivo.objects.exclude(estado__in=['COS', 'FIN'])

    # Feed de últimos movimientos (Mezcla de historial y tareas)
    movimientos_crudos = []

    # A. Movimientos de cultivos (Traspasos, Ediciones, Registros, Cosechas)
    for h in HistorialOperacion.objects.all().order_by('-fecha_hora')[:10]:
        movimientos_crudos.append({
            'accion': f"{h.get_tipo_accion_display()} - Lote {h.lote_id_afectado}",
            'timestamp': h.fecha_hora
        })
    
    # B. Tareas nuevas asignadas
    for t in Tarea.objects.filter(completada=True).order_by('-fecha_completada')[:10]:
        movimientos_crudos.append({
            'accion': f"Tarea asignada: {t.titulo}",
            'timestamp': t.fecha_creacion
        })
    
    # C. Tareas completadas
    for t in Tarea.objects.filter(completada=True).order_by('-fecha_completada')[:10]:
        if t.fecha_completada:
            movimientos_crudos.append({
                'accion': f"Tarea completada: {t.titulo}",
                'timestamp': t.fecha_completada
            })
    
    # Ordenar la mezcla cronológicamente y extraer los 10 más recientes
    movimientos_crudos.sort(key=lambda x: x['timestamp'], reverse=True)
    feed_movimientos = movimientos_crudos[:9]

    # 2. Empaquetar los datos para enviarlos al HTML
    context = {
        'tareas': Tarea.objects.all().order_by('completada', '-prioridad'),
        'insumos': Insumo.objects.all(),
        'registros': HistorialOperacion.objects.filter(tipo_accion='REGISTRO').order_by('-fecha_hora'),

        # Feed mixto
        'feed_movimientos': feed_movimientos,
        
        # Filtros por subsistema
        # Plantinera
        'pla_std': cultivos_activos.filter(subsistema='PLA-STD').order_by('fecha_siembra'),
        'pla_micro': cultivos_activos.filter(subsistema='PLA-MICRO').order_by('fecha_siembra'),
        # Maduración
        'mad_r1': cultivos_activos.filter(subsistema='MAD-R1').order_by('fecha_traspaso_real'),
        'mad_r2': cultivos_activos.filter(subsistema='MAD-R2').order_by('fecha_traspaso_real'),
        'mad_r3': cultivos_activos.filter(subsistema='MAD-R3').order_by('fecha_traspaso_real'),
        'mad_r4': cultivos_activos.filter(subsistema='MAD-R4').order_by('fecha_traspaso_real'),
        # Vertical wall
        'ver_1': cultivos_activos.filter(subsistema='VER-1').order_by('fecha_traspaso_real'),
        'ver_2': cultivos_activos.filter(subsistema='VER-2').order_by('fecha_traspaso_real'),

        # Conteo total para los badges
        'count_pla': cultivos_activos.filter(sistema_produccion='PLA').count(),
        'count_mad': cultivos_activos.filter(sistema_produccion='MAD').count(),
        'count_ver': cultivos_activos.filter(sistema_produccion='VER').count(),
    
        'tab_activa': tab_activa,
    }

    return render(request, 'dashboard.html', context)

# FUNCIONES DE ACCIÓN

def eliminar_cultivo(request, id):
    cultivo = get_object_or_404(Cultivo, id=id)

    if request.method == 'POST':
        # Registrar antes de eliminar el registro
        sistema_donde_estaba = cultivo.subsistema
        cantidad_al_momento = cultivo.cantidad_bandejas
        motivo_formulario = request.POST.get('detalles', '').strip()
        texto_detalles = motivo_formulario if motivo_formulario else f"Eliminado manualmente. Tenía {cantidad_al_momento} plantas/bandejas."

        HistorialOperacion.objects.create(
            tipo_accion='ELIMINACION',
            lote_id_afectado=cultivo.lote_id,
            cultivo_nombre=f"{cultivo.nombre} ({cultivo.variedad})",
            fecha_siembra_registrada=cultivo.fecha_siembra,
            subsistema_previo=sistema_donde_estaba,
            cantidad_anterior=cantidad_al_momento,
            detalles=texto_detalles
        )
        # Eliminar el cultivo
        cultivo.delete()
        
    return redirect('/?tab=cultivos')

def editar_cultivo(request, id):
    cultivo = get_object_or_404(Cultivo, id=id)

    if request.method == 'POST':
        # Datos anteriores
        nombre_anterior = cultivo.nombre
        variedad_anterior = cultivo.variedad
        subsistema_anterior = cultivo.subsistema
        cantidad_anterior = cultivo.cantidad_bandejas
        fecha_anterior = cultivo.fecha_traspaso_real if cultivo.fecha_traspaso_real else cultivo.fecha_siembra

        # Capturar nuevos datos
        nuevo_nombre = request.POST.get('nombre')
        nueva_variedad = request.POST.get('variedad')
        nuevo_subsistema = request.POST.get('subsistema')
        nueva_cantidad = request.POST.get('cantidad_bandejas')
        nueva_fecha_siembra = request.POST.get('fecha_siembra')
        nueva_fecha_traspaso = request.POST.get('fecha_traspaso')

        # Aplicar cambios al cultivo
        cultivo.nombre = nuevo_nombre
        cultivo.variedad = nueva_variedad
        cultivo.subsistema = nuevo_subsistema
        
        if nueva_cantidad and nueva_cantidad.strip():
            cultivo.cantidad_bandejas = int(nueva_cantidad)

        # Asignar el sistema macro en el subsistema
        if 'PLA' in nuevo_subsistema:
            cultivo.sistema_produccion = 'PLA'
        elif 'MAD' in nuevo_subsistema:
            cultivo.sistema_produccion = 'MAD'
        elif 'VER' in nuevo_subsistema:
            cultivo.sistema_produccion = 'VER'

        # Actualizar fechas
        fecha_modificada = fecha_anterior
        if nueva_fecha_siembra and nueva_fecha_siembra.strip():
            cultivo.fecha_siembra = nueva_fecha_siembra
            fecha_modificada = nueva_fecha_siembra

        if nueva_fecha_traspaso and nueva_fecha_traspaso.strip():
            cultivo.fecha_traspaso_real = nueva_fecha_traspaso
            fecha_modificada = nueva_fecha_traspaso

        cultivo.save()

        # Considerar únicamente lo que cambió
        cambios = []
        if nombre_anterior != nuevo_nombre or variedad_anterior != nueva_variedad:
            cambios.append("Cultivo modificado")
        if subsistema_anterior != nuevo_subsistema:
            cambios.append("Ubicación reasignada")
        if str(cantidad_anterior) != str(nueva_cantidad):
            cambios.append("Ajuste de inventario")
        
        # Convertir la fecha vieja a texto para comparar con fecha nueva del HTML
        if str(fecha_anterior) != str(fecha_modificada):
            cambios.append("Fecha ajustada")
        
        texto_detalles = " | ".join(cambios) if cambios else "Edición general de registro"

        # Registrar la operación en el Historial
        HistorialOperacion.objects.create(
            tipo_accion='EDICION',
            lote_id_afectado=cultivo.lote_id,

            # Datos anteriores
            cultivo_nombre_anterior=f"{nombre_anterior} ({variedad_anterior})",
            subsistema_previo=subsistema_anterior,
            cantidad_anterior=cantidad_anterior,
            fecha_anterior=fecha_anterior,

            # Datos nuevos
            cultivo_nombre_nuevo=f"{cultivo.nombre} ({cultivo.variedad})",
            subsistema_posterior=cultivo.subsistema,
            cantidad_posterior=cultivo.cantidad_bandejas,
            fecha_modificada=fecha_modificada,

            # Detalles
            detalles=texto_detalles
        )
    return redirect('/?tab=cultivos')

def traspaso_sistema(request, id):
    # Obtener el cultivo a traspasar
    cultivo = get_object_or_404(Cultivo, id=id)
    if request.method == 'POST':
        ubicacion_anterior = cultivo.subsistema
        nuevo_subsistema = request.POST.get('nuevo_subsistema')
        fecha_traspaso = request.POST.get('fecha_traspaso')
        cantidad = request.POST.get('cantidad_bandejas')
        detalles_registro = request.POST.get('detalles')

        if cantidad is not None and cantidad != '':
            cultivo.cantidad_bandejas = int(cantidad)
        
        # Actualizar el cultivo
        cultivo.subsistema = nuevo_subsistema
        cultivo.fecha_traspaso_real = fecha_traspaso

        # Asignar sistema macro
        if 'MAD' in nuevo_subsistema:
            cultivo.sistema_produccion = 'MAD'
        elif 'VER' in nuevo_subsistema:
            cultivo.sistema_produccion = 'VER'

        cultivo.save()

        # Registrar antes de traspasar el registro
        HistorialOperacion.objects.create(
            tipo_accion='TRASPASO',
            lote_id_afectado=cultivo.lote_id,
            cultivo_nombre=f"{cultivo.nombre} ({cultivo.variedad})",
            fecha_siembra_registrada=cultivo.fecha_siembra,
            fecha_siembra_traspaso=cultivo.fecha_traspaso,
            subsistema_previo=ubicacion_anterior,
            subsistema_posterior=cultivo.subsistema,
            cantidad=cultivo.cantidad_bandejas,
            detalles=detalles_registro,
        )
    return redirect('/?tab=cultivos')

def cosechar_cultivo(request, id):
    cultivo = get_object_or_404(Cultivo, id=id)
    if request.method == 'POST':



        cultivo.estado = 'COS'
        cultivo.save()

        # Registrar antes de cosechar el registro
        HistorialOperacion.objects.create(
            tipo_accion='COSECHA',
            lote_id_afectado=cultivo.lote_id,
            cultivo_nombre=f"{cultivo.nombre} ({cultivo.variedad})",
            detalles=f"Cosechado desde {cultivo.subsistema}. Total: {cultivo.cantidad_bandejas} unidades"
        )
    return redirect('/?tab=cultivos')

def historial(request):
    # Obtener todo el historial
    historial_completo = HistorialOperacion.objects.all().order_by('-fecha_hora')
    context = {
        'registros': historial_completo.filter(tipo_accion='REGISTRO'),
        'traspasos': historial_completo.filter(tipo_accion='TRASPASO'),
        'ediciones': historial_completo.filter(tipo_accion='EDICION'),
        'eliminaciones': historial_completo.filter(tipo_accion='ELIMINACION'),
        'cosechas': historial_completo.filter(tipo_accion='COSECHA'),
    }
    return render(request, 'historial.html', context)

def pagina_tareas(request):
    # Leer si el usuario hace click en los filtros
    filtro_sub = request.GET.get('sub', '')

    # Buscar las tareas pendientes
    pendientes = Tarea.objects.filter(completada=False)
    # Buscar solo las tareas completadas hoy
    hoy = timezone.localdate()
    completadas = Tarea.objects.filter(completada=True, fecha_completada__date=hoy)

    #Filtro inteligente
    if filtro_sub:
        if filtro_sub == 'GENERAL':
            pendientes = pendientes.filter(subsistema='GENERAL')
            completadas = completadas.filter(subsistema='GENERAL')
        else:
            pendientes = pendientes.filter(subsistema__startswith=filtro_sub)
            completadas = completadas.filter(subsistema__startswith=filtro_sub)
    
    # Empaquetar todo ordenado para enviarlo al HTML
    context = {
        'pendientes_alta': pendientes.filter(prioridad='ALTA').order_by('-fecha_creacion'),
        'pendientes_media': pendientes.filter(prioridad='MEDIA').order_by('-fecha_creacion'),
        'pendientes_baja': pendientes.filter(prioridad='BAJA').order_by('-fecha_creacion'),
        'completadas': completadas.order_by('-fecha_completada'),
        'filtro_actual': filtro_sub
    }

    return render(request, 'tareas.html', context)


def completar_tarea(request, tarea_id):
    if request.method == 'POST':
        # Buscar la tarea especifica
        tarea = get_object_or_404(Tarea, id=tarea_id)

        # Cambiar el estado y colocar hora exacta
        tarea.completada = True
        tarea.fecha_completada = timezone.now()
        tarea.save()
    
    return redirect('tareas')

def crear_tarea(request):
    if request.method == 'POST':
        # Capturar datos que escribió el usuario en el modal
        titulo = request.POST.get('titulo')
        subsistema = request.POST.get('subsistema')
        prioridad = request.POST.get('prioridad')
        descripcion = request.POST.get('descripcion')

        # Crear nuevo registro en base de datos
        Tarea.objects.create(
            titulo=titulo,
            subsistema=subsistema,
            prioridad=prioridad,
            descripcion=descripcion,
            completada=False,
            fecha_creacion=timezone.now()
        )
    
    return redirect('tareas')

def editar_tarea(request, tarea_id):
    if request.method == 'POST':
        tarea = get_object_or_404(Tarea, id=tarea_id)

        # Actualizar los datos con lo que venga del formulario
        tarea.titulo = request.POST.get('titulo')
        tarea.subsistema = request.POST.get('subsistema')
        tarea.prioridad = request.POST.get('prioridad')
        tarea.descripcion = request.POST.get('descripcion')

        tarea.save()
    
    return redirect('tareas')

def eliminar_tarea(request, tarea_id):
    if request.method == 'POST':
        tarea = get_object_or_404(Tarea, id=tarea_id)
        tarea.delete()
    
    return redirect('tareas')