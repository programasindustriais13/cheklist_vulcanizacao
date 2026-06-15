from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from core.models import User, Machine, ChecklistSession, ChecklistItemValue, ChecklistTimelineLog

class ChecklistSystemTests(TestCase):
    def setUp(self):
        # Create normal users for different roles (approved/active)
        self.inspector = User.objects.create_user(
            username='test_inspector',
            password='testpassword123',
            specialty='Eletricista',
            is_active=True
        )
        self.leader = User.objects.create_user(
            username='test_leader',
            password='testpassword123',
            specialty='Lider',
            is_active=True
        )
        self.analyst = User.objects.create_user(
            username='test_analyst',
            password='testpassword123',
            specialty='Analista',
            is_active=True
        )
        self.director = User.objects.create_user(
            username='test_director',
            password='testpassword123',
            specialty='Diretor',
            is_active=True
        )
        self.machine = Machine.objects.create(
            name='Test Machine 101',
            description='Test description'
        )

    def test_user_creation_and_specialty(self):
        self.assertEqual(self.inspector.specialty, 'Eletricista')
        self.assertEqual(str(self.inspector), 'test_inspector (Eletricista)')

    def test_user_inactive_on_registration(self):
        # Post to register
        response = self.client.post(reverse('register'), {
            'username': 'new_user',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
            'specialty': 'Mecânico',
            'email': 'new@test.com',
            'first_name': 'New',
            'last_name': 'User'
        })
        # Check redirect to login
        self.assertRedirects(response, reverse('login'))
        
        # Check user created but inactive
        new_user = User.objects.get(username='new_user')
        self.assertFalse(new_user.is_active)

        # Attempt login: check custom message
        response = self.client.post(reverse('login'), {
            'username': 'new_user',
            'password': 'newpassword123'
        })
        self.assertContains(
            response, 
            "Seu cadastro foi realizado com sucesso, mas aguarda a aprovação de um Administrador/Diretor para liberar o acesso."
        )

    def test_user_activation_by_admin(self):
        # Create an inactive user
        inactive_user = User.objects.create_user(
            username='inactive_guy',
            password='password123',
            specialty='Mecânico',
            is_active=False
        )
        # Login as analyst to approve
        self.client.login(username='test_analyst', password='testpassword123')
        
        # Approve user
        response = self.client.post(reverse('approve_user', kwargs={'user_id': inactive_user.id}))
        self.assertRedirects(response, reverse('user_approval_list'))
        
        inactive_user.refresh_from_db()
        self.assertTrue(inactive_user.is_active)

    def test_start_checklist_view(self):
        self.client.login(username='test_inspector', password='testpassword123')
        
        # Post checklist start
        response = self.client.post(reverse('checklist_start'), {
            'machine': self.machine.id,
            'leader': self.leader.id
        })
        
        # Check session was created
        session = ChecklistSession.objects.filter(machine=self.machine, leader=self.leader).first()
        self.assertIsNotNone(session)
        self.assertEqual(session.status, 'IN_PROGRESS')
        self.assertEqual(session.inspector, self.inspector)
        
        # Verify redirect
        self.assertRedirects(response, reverse('checklist_execute', kwargs={'session_id': session.id}))

    def test_leader_blocked_from_starting_checklist(self):
        self.client.login(username='test_leader', password='testpassword123')
        response = self.client.post(reverse('checklist_start'), {
            'machine': self.machine.id,
            'leader': self.leader.id
        })
        self.assertEqual(response.status_code, 403)

    def test_checklist_pause_and_continue(self):
        self.client.login(username='test_inspector', password='testpassword123')
        
        # Create session
        session = ChecklistSession.objects.create(
            machine=self.machine,
            leader=self.leader,
            inspector=self.inspector,
            status='IN_PROGRESS',
            started_at=timezone.now()
        )
        # Create item
        item = ChecklistItemValue.objects.create(
            session=session,
            section='ELETRICA',
            item_name='Test item',
            status=None
        )
        
        # Pause session
        response = self.client.post(
            reverse('checklist_execute', kwargs={'session_id': session.id}),
            {
                'action': 'pause',
                f'status_{item.id}': 'C',
                f'observations_{item.id}': 'Checked conforme'
            }
        )
        
        session.refresh_from_db()
        item.refresh_from_db()
        self.assertEqual(session.status, 'PAUSED')
        self.assertEqual(item.status, 'C')
        self.assertEqual(item.observations, 'Checked conforme')
        
        # Continue session
        response = self.client.post(
            reverse('checklist_execute', kwargs={'session_id': session.id}),
            {
                'action': 'continue'
            }
        )
        
        session.refresh_from_db()
        self.assertEqual(session.status, 'IN_PROGRESS')

    def test_checklist_validation_and_finalize_to_leader(self):
        self.client.login(username='test_inspector', password='testpassword123')
        
        session = ChecklistSession.objects.create(
            machine=self.machine,
            leader=self.leader,
            inspector=self.inspector,
            status='IN_PROGRESS',
            started_at=timezone.now()
        )
        item1 = ChecklistItemValue.objects.create(
            session=session,
            section='ELETRICA',
            item_name='Test item 1',
            status=None
        )
        
        # Post finalize (success)
        response = self.client.post(
            reverse('checklist_execute', kwargs={'session_id': session.id}),
            {
                'action': 'finalize',
                f'status_{item1.id}': 'C',
                f'observations_{item1.id}': ''
            }
        )
        session.refresh_from_db()
        # Should now be AGUARDANDO_LIDER, not COMPLETED
        self.assertEqual(session.status, 'AGUARDANDO_LIDER')
        self.assertRedirects(response, reverse('dashboard'))

    def test_leader_and_analyst_approval_workflow(self):
        # 1. Setup session finalized by inspector (starts in AGUARDANDO_LIDER)
        session = ChecklistSession.objects.create(
            machine=self.machine,
            leader=self.leader,
            inspector=self.inspector,
            status='AGUARDANDO_LIDER',
            started_at=timezone.now()
        )
        ChecklistItemValue.objects.create(
            session=session,
            section='ELETRICA',
            item_name='Test item',
            status='C'
        )

        # 2. Leader approves -> APROVADO
        self.client.login(username='test_leader', password='testpassword123')
        response = self.client.post(reverse('leader_decision', kwargs={'session_id': session.id}), {
            'decision': 'approve'
        })
        self.assertRedirects(response, reverse('dashboard'))
        session.refresh_from_db()
        self.assertEqual(session.status, 'APROVADO')

        # 3. Leader rejects -> REPROVADO_LIDER
        session.status = 'AGUARDANDO_LIDER'
        session.save()
        response = self.client.post(reverse('leader_decision', kwargs={'session_id': session.id}), {
            'decision': 'reject'
        })
        session.refresh_from_db()
        self.assertEqual(session.status, 'REPROVADO_LIDER')

        # 4. Analyst approves (override) -> APROVADO
        self.client.login(username='test_analyst', password='testpassword123')
        response = self.client.post(reverse('analyst_decision', kwargs={'session_id': session.id}), {
            'decision': 'approve'
        })
        session.refresh_from_db()
        self.assertEqual(session.status, 'APROVADO')

        # 5. Analyst rejects -> REPROVAR_FINAL_REFAZER
        session.status = 'REPROVADO_LIDER'
        session.save()
        response = self.client.post(reverse('analyst_decision', kwargs={'session_id': session.id}), {
            'decision': 'reject'
        })
        session.refresh_from_db()
        self.assertEqual(session.status, 'REPROVAR_FINAL_REFAZER')

        # 6. Reopen by technician -> IN_PROGRESS
        self.client.login(username='test_inspector', password='testpassword123')
        response = self.client.post(reverse('checklist_reopen', kwargs={'session_id': session.id}))
        self.assertRedirects(response, reverse('checklist_execute', kwargs={'session_id': session.id}))
        session.refresh_from_db()
        self.assertEqual(session.status, 'IN_PROGRESS')

    def test_excel_export_restricted_for_technician(self):
        # Create completed/approved checklist
        session = ChecklistSession.objects.create(
            machine=self.machine,
            leader=self.leader,
            inspector=self.inspector,
            status='APROVADO',
            started_at=timezone.now(),
            completed_at=timezone.now()
        )
        ChecklistItemValue.objects.create(
            session=session,
            section='ELETRICA',
            item_name='Test item',
            status='C'
        )

        # Login as technician -> Should be blocked (403)
        self.client.login(username='test_inspector', password='testpassword123')
        response = self.client.get(reverse('export_checklist_excel', kwargs={'session_id': session.id}))
        self.assertEqual(response.status_code, 403)

        # Login as analyst -> Should be allowed (200)
        self.client.login(username='test_analyst', password='testpassword123')
        response = self.client.get(reverse('export_checklist_excel', kwargs={'session_id': session.id}))
        self.assertEqual(response.status_code, 200)
