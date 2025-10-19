from django import forms
from .models import Torneo, Equipo, Jugador, Partido


class TorneoForm(forms.ModelForm):
    class Meta:
        model = Torneo
        fields = ["nombre", "fecha_inicio", "fecha_fin", "ubicacion", "descripcion"]
        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date"}),
        }

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ["torneo", "nombre"]

class JugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador
        fields = ["equipo", "nombre", "dorsal", "email"]

class PartidoForm(forms.ModelForm):
    class Meta:
        model = Partido
        # Partido entre EQUIPOS (no jugadores)
        fields = ["torneo", "equipo1", "equipo2", "fecha", "estado", "marcador1", "marcador2"]
        widgets = {
            "fecha": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si hay torneo seleccionado (en POST o instancia), filtra los equipos a ese torneo
        torneo_id = None
        if self.data.get("torneo"):
            torneo_id = self.data.get("torneo")
        elif self.instance and self.instance.pk:
            torneo_id = self.instance.torneo_id

        if torneo_id:
            self.fields["equipo1"].queryset = Equipo.objects.filter(torneo_id=torneo_id)
            self.fields["equipo2"].queryset = Equipo.objects.filter(torneo_id=torneo_id)
