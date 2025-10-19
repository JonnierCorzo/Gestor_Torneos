from django.db import models, transaction
from django.core.exceptions import ValidationError

class Torneo(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    ubicacion = models.CharField(max_length=150, blank=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ["-fecha_inicio", "nombre"]

    def __str__(self):
        return self.nombre


class Equipo(models.Model):
    MAX_EQUIPOS_POR_TORNEO = 20

    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name="equipos")
    nombre = models.CharField(max_length=120)

    class Meta:
        # Evita dos equipos con el mismo nombre dentro del mismo torneo
        constraints = [
            models.UniqueConstraint(
                fields=["torneo", "nombre"], name="unique_equipo_en_torneo"
            )
        ]
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.torneo.nombre})"

    def clean(self):
        """
        Valida el límite de 20 equipos por torneo.
        Se salta la validación si el objeto ya existe y no cambia de torneo,
        para permitir editar el nombre sin bloquear por el conteo.
        """
        super().clean()
        if self.pk and not self._state.adding:
            # Si se está editando, sólo validamos si cambiaron de torneo
            try:
                original = Equipo.objects.get(pk=self.pk)
            except Equipo.DoesNotExist:
                original = None
            cambio_de_torneo = original and original.torneo_id != self.torneo_id
            if not cambio_de_torneo:
                return

        # Nueva creación o cambio de torneo: validar cupo
        cuenta = Equipo.objects.filter(torneo=self.torneo).exclude(pk=self.pk).count()
        if cuenta >= self.MAX_EQUIPOS_POR_TORNEO:
            raise ValidationError(
                f"El torneo '{self.torneo}' ya tiene {self.MAX_EQUIPOS_POR_TORNEO} equipos (límite máximo)."
            )

    def save(self, *args, **kwargs):
        # Asegura que se ejecute clean() incluso si no se usa ModelForm
        self.full_clean()
        return super().save(*args, **kwargs)


class Jugador(models.Model):
    MAX_JUGADORES_POR_EQUIPO = 15

    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name="jugadores", null=True, blank=True)
    nombre = models.CharField(max_length=120)
    dorsal = models.PositiveIntegerField(null=True, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        # Evita jugadores duplicados por nombre dentro del mismo equipo
        constraints = [
            models.UniqueConstraint(
                fields=["equipo", "nombre"], name="unique_jugador_en_equipo"
            )
        ]
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} - {self.equipo.nombre}"

    def clean(self):
        super().clean()
        if self.pk and not self._state.adding:
            # edición: no validar conteo si no cambia de equipo
            try:
                original = Jugador.objects.get(pk=self.pk)
            except Jugador.DoesNotExist:
                original = None
            cambio_de_equipo = original and original.equipo_id != self.equipo_id
            if not cambio_de_equipo:
                return

        cuenta = Jugador.objects.filter(equipo=self.equipo).exclude(pk=self.pk).count()
        if cuenta >= self.MAX_JUGADORES_POR_EQUIPO:
            raise ValidationError(
                f"El equipo '{self.equipo}' ya tiene {self.MAX_JUGADORES_POR_EQUIPO} jugadores (límite máximo)."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
    
class Partido(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("jugado", "Jugado"),
    ]

    torneo = models.ForeignKey("Torneo", on_delete=models.CASCADE, related_name="partidos")
    equipo1 = models.ForeignKey(Equipo, on_delete=models.CASCADE,
                            related_name="partidos_equipo1",
                            null=True, blank=True)
    equipo2 = models.ForeignKey(Equipo, on_delete=models.CASCADE,
                            related_name="partidos_equipo2",
                            null=True, blank=True)
    fecha = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    # Si luego quieres marcador por equipo:
    marcador1 = models.PositiveIntegerField(null=True, blank=True)
    marcador2 = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha", "-id"]

    def clean(self):
        # Validaciones: equipos distintos y del mismo torneo
        if self.equipo1_id and self.equipo2_id and self.equipo1_id == self.equipo2_id:
            raise ValidationError("Un partido necesita dos equipos distintos.")
        if self.equipo1 and self.equipo2 and self.equipo1.torneo_id != self.equipo2.torneo_id:
            raise ValidationError("Ambos equipos deben pertenecer al mismo torneo.")
        # Coherencia de torneo con equipos
        if self.torneo and self.equipo1 and self.torneo_id != self.equipo1.torneo_id:
            raise ValidationError("El torneo del partido debe coincidir con el torneo del Equipo 1.")
        if self.torneo and self.equipo2 and self.torneo_id != self.equipo2.torneo_id:
            raise ValidationError("El torneo del partido debe coincidir con el torneo del Equipo 2.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        if self.equipo1_id and self.equipo2_id:
            return f"{self.equipo1.nombre} vs {self.equipo2.nombre} ({self.torneo.nombre})"
        return f"Partido {self.pk or ''}"
