from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    SPECIALTY_CHOICES = [
        ('Eletricista', 'Eletricista'),
        ('Mecânico', 'Mecânico'),
        ('Eletromecânico', 'Eletromecânico'),
        ('Analista', 'Analista'),
        ('Diretor', 'Diretor'),
        ('Lider', 'Lider'),
    ]
    specialty = models.CharField(max_length=50, choices=SPECIALTY_CHOICES, verbose_name='Especialidade')
    partner_user = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partner_of',
        verbose_name='Parceiro de Turno'
    )

    @property
    def is_technician(self):
        return self.specialty in ['Eletricista', 'Mecânico', 'Eletromecânico']

    @property
    def is_analyst(self):
        return self.specialty == 'Analista'

    @property
    def is_director(self):
        return self.specialty == 'Diretor'

    @property
    def is_leader(self):
        return self.specialty == 'Lider'

    @property
    def can_export_excel(self):
        return self.specialty in ['Diretor', 'Analista'] or self.is_superuser

    @property
    def can_create_checklist(self):
        return self.specialty != 'Lider' or self.is_superuser

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.partner_user:
            partner = self.partner_user
            if partner.partner_user != self:
                partner.partner_user = self
                super(User, partner).save(update_fields=['partner_user'])
        
        other_partners = User.objects.filter(partner_user=self)
        if self.partner_user:
            other_partners = other_partners.exclude(id=self.partner_user.id)
        for other in other_partners:
            other.partner_user = None
            super(User, other).save(update_fields=['partner_user'])

    def __str__(self):
        return f"{self.username} ({self.specialty})"

class Machine(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nome da Máquina')
    description = models.TextField(blank=True, null=True, verbose_name='Descrição')

    def __str__(self):
        return self.name

class ChecklistSession(models.Model):
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Não Iniciado'),
        ('IN_PROGRESS', 'Em Andamento'),
        ('PAUSED', 'Pausado'),
        ('COMPLETED', 'Finalizado'),
        ('AGUARDANDO_LIDER', 'Aguardando Líder'),
        ('APROVADO', 'Aprovado'),
        ('REPROVADO_LIDER', 'Reprovado pelo Líder'),
        ('REPROVAR_FINAL_REFAZER', 'Reprovado Final - Refazer'),
    ]
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='sessions', verbose_name='Máquina')
    leader = models.ForeignKey(User, on_delete=models.PROTECT, related_name='led_sessions', verbose_name='Líder de Turno', null=True)
    inspector = models.ForeignKey(User, on_delete=models.PROTECT, related_name='inspections', verbose_name='Inspetor')
    co_inspector = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='co_inspections',
        verbose_name='Co-Inspetor'
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='NOT_STARTED', verbose_name='Status')
    general_observations = models.TextField(null=True, blank=True, verbose_name='Observações Gerais (Estado da Máquina)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Iniciado em')
    paused_at = models.DateTimeField(null=True, blank=True, verbose_name='Pausado em')
    resumed_at = models.DateTimeField(null=True, blank=True, verbose_name='Retomado em')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Finalizado em')

    def __str__(self):
        return f"Checklist #{self.id} - {self.machine.name} ({self.status})"

class ChecklistTimelineLog(models.Model):
    ACTION_CHOICES = [
        ('START', 'Iniciar'),
        ('PAUSE', 'Pausar'),
        ('CONTINUE', 'Continuar'),
        ('FINISH', 'Finalizar'),
        ('REOPEN', 'Reabrir para Ajustes'),
        ('APPROVE_LIDER', 'Aprovar pelo Líder'),
        ('REJECT_LIDER', 'Reprovar pelo Líder'),
        ('APPROVE_ANALISTA', 'Aprovar pelo Analista'),
        ('REJECT_ANALISTA', 'Reprovar pelo Analista'),
    ]
    session = models.ForeignKey(ChecklistSession, on_delete=models.CASCADE, related_name='timeline_logs', verbose_name='Sessão')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Usuário')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='Ação')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora')
    pause_reason = models.TextField(null=True, blank=True, verbose_name='Motivo da Pausa')

    def __str__(self):
        return f"{self.session.id} - {self.action} por {self.user.username if self.user else 'Desconhecido'} em {self.timestamp}"

class ChecklistItemValue(models.Model):
    SECTION_CHOICES = [
        ('HIDRAULICA', 'Hidráulica (Mecânico)'),
        ('PNEUMATICA', 'Pneumática (Mecânico)'),
        ('SISTEMA_VULCANIZACAO', 'Sistema de Vulcanização (Mecânico)'),
        ('SISTEMA_VAPOR', 'Sistema de Vapor (Mecânico)'),
        ('ESTRUTURA', 'Estrutura (Mecânico)'),
        ('ELETRICA', 'Elétrica (Eletricista)'),
    ]
    STATUS_CHOICES = [
        ('C', 'Conforme'),
        ('NC', 'Não Conforme'),
    ]
    session = models.ForeignKey(ChecklistSession, on_delete=models.CASCADE, related_name='items', verbose_name='Sessão')
    section = models.CharField(max_length=30, choices=SECTION_CHOICES, verbose_name='Seção')
    item_name = models.CharField(max_length=255, verbose_name='Nome do Item')
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, null=True, blank=True, verbose_name='Status')
    observations = models.TextField(null=True, blank=True, verbose_name='Observações')

    def __str__(self):
        return f"{self.section} - {self.item_name}: {self.status or 'Sem resposta'}"
