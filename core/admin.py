from django.contrib import admin
from .models import Torneo, Equipo, Jugador


class EquipoInline(admin.TabularInline):
    model = Equipo
    extra = 0
    max_num = Equipo.MAX_EQUIPOS_POR_TORNEO  # UI limita a 20

class JugadorInline(admin.TabularInline):
    model = Jugador
    extra = 0
    max_num = Jugador.MAX_JUGADORES_POR_EQUIPO  # UI limita a 15

@admin.register(Torneo)
class TorneoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "fecha_inicio", "fecha_fin", "ubicacion")
    inlines = [EquipoInline]

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "torneo")
    list_filter = ("torneo",)
    search_fields = ("nombre", "torneo__nombre")
    inlines = [JugadorInline]

@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "equipo", "dorsal", "email")
    list_filter = ("equipo__torneo", "equipo")
    search_fields = ("nombre", "equipo__nombre")


