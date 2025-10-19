from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from .models import Torneo, Jugador, Equipo,Partido
from .forms import TorneoForm, JugadorForm, PartidoForm, EquipoForm
from django.db.models import Q


def home(request):
    return render(request, "core/home.html")

@login_required
def torneos_list(request):
    q = request.GET.get("q", "")
    torneos = Torneo.objects.all()
    if q:
        torneos = torneos.filter(nombre__icontains=q)
    return render(request, "core/torneos_list.html", {"torneos": torneos, "q": q})

@login_required
def torneo_detail(request, pk):
    torneo = get_object_or_404(Torneo, pk=pk)
    return render(request, "core/torneo_detail.html", {"torneo": torneo})

@login_required
def torneo_create(request):
    if request.method == "POST":
        form = TorneoForm(request.POST)
        if form.is_valid():
            torneo = form.save()
            messages.success(request, "Torneo creado correctamente.")
            return redirect(reverse("torneo_detail", args=[torneo.pk]))
    else:
        form = TorneoForm()
    return render(request, "core/torneo_form.html", {"form": form, "modo": "crear"})

@login_required
def torneo_update(request, pk):
    torneo = get_object_or_404(Torneo, pk=pk)
    if request.method == "POST":
        form = TorneoForm(request.POST, instance=torneo)
        if form.is_valid():
            form.save()
            messages.success(request, "Torneo actualizado.")
            return redirect(reverse("torneo_detail", args=[torneo.pk]))
    else:
        form = TorneoForm(instance=torneo)
    return render(request, "core/torneo_form.html", {"form": form, "modo": "editar", "torneo": torneo})

@login_required
def torneo_delete(request, pk):
    torneo = get_object_or_404(Torneo, pk=pk)
    if request.method == "POST":
        torneo.delete()
        messages.success(request, "Torneo eliminado.")
        return redirect("torneos_list")
    return render(request, "core/torneo_confirm_delete.html", {"torneo": torneo})

@login_required
def jugadores_list(request):
    torneo_id = request.GET.get("torneo") or ""
    equipo_id = request.GET.get("equipo") or ""

    
    jugadores = Jugador.objects.select_related("equipo", "equipo__torneo")

    
    torneos = Torneo.objects.all().order_by("nombre")
    if torneo_id:
        equipos = Equipo.objects.filter(torneo_id=torneo_id).order_by("nombre")
        jugadores = jugadores.filter(equipo__torneo_id=torneo_id)
    else:
        equipos = Equipo.objects.all().order_by("nombre")

    if equipo_id:
        jugadores = jugadores.filter(equipo_id=equipo_id)

    ctx = {
        "jugadores": jugadores,
        "torneos": torneos,
        "equipos": equipos,
        "torneo_id": str(torneo_id),
        "equipo_id": str(equipo_id),
    }
    return render(request, "core/jugadores_list.html", ctx)
    

@login_required
def jugador_create(request):
    if request.method == "POST":
        form = JugadorForm(request.POST)
        if form.is_valid():
            j = form.save()
            messages.success(request, "Jugador creado.")
            # Vuelve al listado respetando filtros (por torneo)
            return redirect(reverse("jugadores_list") + f"?torneo={j.equipo.torneo_id}&equipo={j.equipo_id}")
    else:
        initial = {}
        # si vienen ?torneo y/o ?equipo en la URL, precarga
        torneo_id = request.GET.get("torneo")
        equipo_id = request.GET.get("equipo")
        if equipo_id:
            initial["equipo"] = equipo_id
        form = JugadorForm(initial=initial)
        # (opcional) si quieres filtrar el queryset de equipos del form por torneo:
        if torneo_id:
            form.fields["equipo"].queryset = Equipo.objects.filter(torneo_id=torneo_id)

    return render(request, "core/jugador_form.html", {"form": form})

# PARTIDOS

@login_required
def partidos_list(request):
    torneo_id = request.GET.get("torneo") or ""
    equipo_id = request.GET.get("equipo") or ""

    partidos = Partido.objects.select_related("torneo", "equipo1", "equipo2")
    torneos = Torneo.objects.all().order_by("nombre")
    equipos = Equipo.objects.all().order_by("nombre")

    if torneo_id:
        partidos = partidos.filter(torneo_id=torneo_id)
        equipos = equipos.filter(torneo_id=torneo_id)

    if equipo_id:
        partidos = partidos.filter(Q(equipo1_id=equipo_id) | Q(equipo2_id=equipo_id))

    ctx = {
        "partidos": partidos.order_by("fecha", "id"),
        "torneos": torneos,
        "equipos": equipos,
        "torneo_id": str(torneo_id),
        "equipo_id": str(equipo_id),
    }
    return render(request, "core/partidos_list.html", ctx)

@login_required
def partido_create(request):
    if request.method == "POST":
        form = PartidoForm(request.POST)
        if form.is_valid():
            p = form.save()
            messages.success(request, "Partido creado.")
            return redirect(reverse("partidos_list") + f"?torneo={p.torneo_id}")
    else:
        initial = {}
        t = request.GET.get("torneo")
        if t:
            initial["torneo"] = t
        form = PartidoForm(initial=initial)
    return render(request, "core/partido_form.html", {"form": form})

@login_required
def partido_update(request, pk):
    p = get_object_or_404(Partido, pk=pk)
    if request.method == "POST":
        form = PartidoForm(request.POST, instance=p)
        if form.is_valid():
            p = form.save()
            messages.success(request, "Partido actualizado.")
            return redirect(reverse("partidos_list") + f"?torneo={p.torneo_id}")
    else:
        form = PartidoForm(instance=p)
    return render(request, "core/partido_form.html", {"form": form})

@login_required
def partido_set_resultado(request, pk):
    """Vista rápida para marcar como 'jugado' y poner marcador/fecha."""
    p = get_object_or_404(Partido, pk=pk)
    if request.method == "POST":
        p.marcador1 = int(request.POST.get("marcador1") or 0)
        p.marcador2 = int(request.POST.get("marcador2") or 0)
        fecha_str = request.POST.get("fecha")
        if fecha_str:
            # from input type=datetime-local (YYYY-MM-DDTHH:MM)
            p.fecha = datetime.fromisoformat(fecha_str)
        p.estado = "jugado"
        p.save()
        messages.success(request, "Resultado guardado.")
        return redirect(reverse("partidos_list") + f"?torneo={p.torneo_id}")
    return render(request, "core/partido_set_resultado.html", {"p": p})

@transaction.atomic
@login_required
def partidos_generar(request):
    """
    Genera fixture round-robin para un torneo: todos contra todos una vez.
    Si deseas ida y vuelta, cambia ida_vuelta=True.
    Asigna fechas cada 7 días empezando hoy si no indicas otra cosa.
    """
    torneo_id = request.GET.get("torneo")
    if not torneo_id:
        messages.error(request, "Debes seleccionar un torneo (?torneo=ID).")
        return redirect("partidos_list")

    torneo = get_object_or_404(Torneo, pk=torneo_id)
    equipos = list(Equipo.objects.filter(torneo=torneo).order_by("id"))
    n = len(equipos)
    if n < 2:
        messages.error(request, "Se necesitan al menos 2 equipos en el torneo.")
        return redirect(reverse("partidos_list") + f"?torneo={torneo.id}")

    ida_vuelta = False  # cambia a True si quieres doble ronda
    start_date = datetime.now().replace(microsecond=0, second=0, minute=0)  # hoy a la hora redondeada
    delta = timedelta(days=7)  # cada jornada, 7 días después

    # Algoritmo círculo (round-robin)
    # si impar, agregamos "bye" (None)
    bye = None
    es_impar = (n % 2 == 1)
    if es_impar:
        equipos.append(bye)
        n += 1

    jornadas = n - 1
    mitad = n // 2
    arr = equipos[:]

    created = 0
    fecha = start_date
    for ronda in range(jornadas):
        parejas = []
        for i in range(mitad):
            a = arr[i]
            b = arr[-(i+1)]
            if a is not None and b is not None:
                parejas.append((a, b))
        # crear partidos de esta ronda
        for (e1, e2) in parejas:
            # normaliza orden por id para respetar la unique constraint
            e1n, e2n = (e1, e2) if e1.id < e2.id else (e2, e1)
            # evita duplicados si ya existen
            if not Partido.objects.filter(torneo=torneo, equipo1=e1n, equipo2=e2n).exists():
                Partido.objects.create(torneo=torneo, equipo1=e1n, equipo2=e2n, fecha=fecha, estado="pendiente")
                created += 1
            if ida_vuelta:
                # segundo partido invertido (otra fecha)
                fecha2 = fecha + timedelta(days=3)  # misma semana
                if not Partido.objects.filter(torneo=torneo, equipo1=e2n, equipo2=e1n).exists():
                    Partido.objects.create(torneo=torneo, equipo1=e2n, equipo2=e1n, fecha=fecha2, estado="pendiente")
                    created += 1
        # rotación
        arr = [arr[0]] + [arr[-1]] + arr[1:-1]
        fecha += delta

    messages.success(request, f"Fixture generado: {created} partidos.")
    return redirect(reverse("partidos_list") + f"?torneo={torneo.id}")
    
@login_required
def equipo_create(request):
    if request.method == "POST":
        form = EquipoForm(request.POST)
        if form.is_valid():
            equipo = form.save()  # valida límite de 20 en clean()
            messages.success(request, "Equipo creado correctamente.")
            return redirect(reverse("equipos_list") + f"?torneo={equipo.torneo_id}")
    else:
        # si vienes con ?torneo=ID, lo ponemos como initial
        initial = {}
        t = request.GET.get("torneo")
        if t:
            initial["torneo"] = t
        form = EquipoForm(initial=initial)
    return render(request, "core/equipo_form.html", {"form": form})

@login_required
def equipo_update(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    if request.method == "POST":
        form = EquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            equipo = form.save()
            messages.success(request, "Equipo actualizado.")
            return redirect(reverse("equipos_list") + f"?torneo={equipo.torneo_id}")
    else:
        form = EquipoForm(instance=equipo)
    return render(request, "core/equipo_form.html", {"form": form})


@login_required
def equipo_delete(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    if request.method == "POST":
        torneo_id = equipo.torneo_id
        equipo.delete()
        messages.success(request, "Equipo eliminado.")
        return redirect(reverse("equipos_list") + f"?torneo={torneo_id}")
    return render(request, "core/equipo_confirm_delete.html", {"equipo": equipo})

@login_required
def equipos_list(request):
    torneo_id = request.GET.get("torneo")
    torneos = Torneo.objects.all()
    equipos = Equipo.objects.select_related("torneo")
    if torneo_id:
        equipos = equipos.filter(torneo_id=torneo_id)
    return render(request, "core/equipos_list.html", {
        "equipos": equipos,
        "torneos": torneos,
        "torneo_id": torneo_id,
    })
