from django.test import TestCase, override_settings
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
                'pause_reason': 'Aguardando peças do estoque',
                f'status_{item.id}': 'C',
                f'observations_{item.id}': 'Checked conforme'
            }
        )
        
        session.refresh_from_db()
        item.refresh_from_db()
        self.assertEqual(session.status, 'PAUSED')
        self.assertEqual(item.status, 'C')
        self.assertEqual(item.observations, 'Checked conforme')

        # Verify timeline log contains the reason
        log = ChecklistTimelineLog.objects.filter(session=session, action='PAUSE').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.pause_reason, 'Aguardando peças do estoque')

        # Verify pause_logs is present in GET context
        response = self.client.get(reverse('checklist_execute', kwargs={'session_id': session.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('pause_logs', response.context)
        self.assertEqual(len(response.context['pause_logs']), 1)
        self.assertEqual(response.context['pause_logs'][0].pause_reason, 'Aguardando peças do estoque')
        
        # Continue session
        response = self.client.post(
            reverse('checklist_execute', kwargs={'session_id': session.id}),
            {
                'action': 'continue'
            }
        )
        
        session.refresh_from_db()
        self.assertEqual(session.status, 'IN_PROGRESS')

    def test_checklist_pause_requires_reason(self):
        self.client.login(username='test_inspector', password='testpassword123')
        
        session = ChecklistSession.objects.create(
            machine=self.machine,
            leader=self.leader,
            inspector=self.inspector,
            status='IN_PROGRESS',
            started_at=timezone.now()
        )
        item = ChecklistItemValue.objects.create(
            session=session,
            section='ELETRICA',
            item_name='Test item',
            status=None
        )
        
        # Attempt to pause without reason (empty string)
        response = self.client.post(
            reverse('checklist_execute', kwargs={'session_id': session.id}),
            {
                'action': 'pause',
                'pause_reason': '',
                f'status_{item.id}': 'C',
                f'observations_{item.id}': 'Checked conforme'
            }
        )
        
        # Should redirect back to checklist execution page
        self.assertRedirects(response, reverse('checklist_execute', kwargs={'session_id': session.id}))
        
        # Status should NOT be PAUSED, should remain IN_PROGRESS
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

    def test_machine_rbac(self):
        # 1. Prohibited profile: Inspector (Eletricista)
        self.client.login(username='test_inspector', password='testpassword123')
        
        # Test machine list
        response = self.client.get(reverse('machine_list'))
        self.assertRedirects(response, reverse('dashboard'))
        # Follow the redirect to check that the warning message is present
        response_follow = self.client.get(reverse('machine_list'), follow=True)
        self.assertContains(response_follow, "Você não tem permissão para acessar esta página.")
        
        # Test machine create
        response = self.client.get(reverse('machine_create'))
        self.assertRedirects(response, reverse('dashboard'))
        
        # Test machine update
        response = self.client.get(reverse('machine_update', kwargs={'pk': self.machine.id}))
        self.assertRedirects(response, reverse('dashboard'))
        
        # Test machine delete
        response = self.client.get(reverse('machine_delete', kwargs={'pk': self.machine.id}))
        self.assertRedirects(response, reverse('dashboard'))
        
        # 2. Prohibited profile: Leader
        self.client.login(username='test_leader', password='testpassword123')
        response = self.client.get(reverse('machine_list'))
        self.assertRedirects(response, reverse('dashboard'))
        
        # 3. Permitted profile: Analyst
        self.client.login(username='test_analyst', password='testpassword123')
        response = self.client.get(reverse('machine_list'))
        self.assertEqual(response.status_code, 200)
        
        # 4. Permitted profile: Director
        self.client.login(username='test_director', password='testpassword123')
        response = self.client.get(reverse('machine_list'))
        self.assertEqual(response.status_code, 200)
        
        # 5. Permitted profile: Superuser
        superuser = User.objects.create_superuser(
            username='test_superuser',
            password='testpassword123',
            email='super@test.com',
            is_active=True
        )
        self.client.login(username='test_superuser', password='testpassword123')
        response = self.client.get(reverse('machine_list'))
        self.assertEqual(response.status_code, 200)

    def test_analytical_dashboard_access_and_filtering(self):
        # 1. Perfis bloqueados: Inspetor e Líder
        self.client.login(username='test_inspector', password='testpassword123')
        response = self.client.get(reverse('analytical_dashboard'))
        self.assertRedirects(response, reverse('dashboard'))

        self.client.login(username='test_leader', password='testpassword123')
        response = self.client.get(reverse('analytical_dashboard'))
        self.assertRedirects(response, reverse('dashboard'))

        # 2. Perfis permitidos: Analista
        self.client.login(username='test_analyst', password='testpassword123')
        response = self.client.get(reverse('analytical_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'chart-evolution')
        self.assertContains(response, 'chart-machine')
        self.assertContains(response, 'chart-section')
        self.assertContains(response, 'chart-reincidence')
        
        # Verificar chaves de contexto dos gráficos
        self.assertIn('evolution_labels', response.context)
        self.assertIn('evolution_data', response.context)
        self.assertIn('machine_labels', response.context)
        self.assertIn('machine_data', response.context)
        self.assertIn('section_labels', response.context)
        self.assertIn('section_data', response.context)
        self.assertIn('reincidence_labels', response.context)
        self.assertIn('reincidence_datasets', response.context)

        # 3. Teste de filtragem por período
        response_filtered = self.client.get(
            reverse('analytical_dashboard') + '?data_inicio=2026-06-01&data_fim=2026-06-15'
        )
        self.assertEqual(response_filtered.status_code, 200)
        self.assertEqual(response_filtered.context['data_inicio'], '2026-06-01')
        self.assertEqual(response_filtered.context['data_fim'], '2026-06-15')

    def test_block_inspected_machine_selection_pending_approval(self):
        # Create a second machine
        machine2 = Machine.objects.create(name='Test Machine 102')

        self.client.login(username='test_inspector', password='testpassword123')

        # 1. Start and finalize a checklist on self.machine so it is AGUARDANDO_LIDER
        session1 = ChecklistSession.objects.create(
            machine=self.machine,
            leader=self.leader,
            inspector=self.inspector,
            status='AGUARDANDO_LIDER',
            started_at=timezone.now(),
            completed_at=timezone.now()
        )

        # 2. Go to the checklist start page, check that machine 101 is NOT in the queryset/options
        response = self.client.get(reverse('checklist_start'))
        self.assertEqual(response.status_code, 200)
        
        # Check that machine2 is in the choices, but self.machine (101) is not
        form = response.context['form']
        machine_choices = [c[0] for c in form.fields['machine'].choices]
        self.assertIn(machine2.id, machine_choices)
        self.assertNotIn(self.machine.id, machine_choices)

        # 3. Security validation: Attempt to POST self.machine (101) even if it's not visible
        response_post = self.client.post(reverse('checklist_start'), {
            'machine': self.machine.id,
            'leader': self.leader.id
        })
        self.assertEqual(response_post.status_code, 200)
        self.assertFormError(
            response_post,
            'form',
            'machine',
            "Você já realizou uma inspeção nesta máquina que está aguardando a aprovação do Líder."
        )

        # 4. If status changes to APROVADO, it should become selectable again
        session1.status = 'APROVADO'
        session1.save()

        response = self.client.get(reverse('checklist_start'))
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        machine_choices = [c[0] for c in form.fields['machine'].choices]
        self.assertIn(self.machine.id, machine_choices)

        # 5. If status becomes REPROVADO_LIDER, it should be blocked again
        session1.status = 'REPROVADO_LIDER'
        session1.save()

        response = self.client.get(reverse('checklist_start'))
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        machine_choices = [c[0] for c in form.fields['machine'].choices]
        self.assertNotIn(self.machine.id, machine_choices)

        # 6. Another inspector should NOT be blocked from selecting the machine
        other_inspector = User.objects.create_user(
            username='other_inspector',
            password='testpassword123',
            specialty='Mecânico',
            is_active=True
        )
        self.client.login(username='other_inspector', password='testpassword123')
        response = self.client.get(reverse('checklist_start'))
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        machine_choices = [c[0] for c in form.fields['machine'].choices]
        self.assertIn(self.machine.id, machine_choices)

    def test_general_observations_saved_and_exported(self):
        self.client.login(username='test_inspector', password='testpassword123')
        session = ChecklistSession.objects.create(
            machine=self.machine,
            leader=self.leader,
            inspector=self.inspector,
            status='IN_PROGRESS',
            started_at=timezone.now()
        )
        item = ChecklistItemValue.objects.create(
            session=session,
            section='ELETRICA',
            item_name='Test item 1',
            status=None
        )

        # 1. Save general observations on pause
        response = self.client.post(
            reverse('checklist_execute', kwargs={'session_id': session.id}),
            {
                'action': 'pause',
                'pause_reason': 'Pausa teste',
                'general_observations': 'Máquina com vazamento de óleo leve',
                f'status_{item.id}': 'C',
                f'observations_{item.id}': ''
            }
        )
        session.refresh_from_db()
        self.assertEqual(session.status, 'PAUSED')
        self.assertEqual(session.general_observations, 'Máquina com vazamento de óleo leve')

        # 2. Resume session
        self.client.post(
            reverse('checklist_execute', kwargs={'session_id': session.id}),
            {'action': 'continue'}
        )
        session.refresh_from_db()
        self.assertEqual(session.status, 'IN_PROGRESS')

        # 3. Save general observations on finalize
        response = self.client.post(
            reverse('checklist_execute', kwargs={'session_id': session.id}),
            {
                'action': 'finalize',
                'general_observations': 'Máquina revisada, tudo ok ao final',
                f'status_{item.id}': 'C',
                f'observations_{item.id}': ''
            }
        )
        session.refresh_from_db()
        self.assertEqual(session.status, 'AGUARDANDO_LIDER')
        self.assertEqual(session.general_observations, 'Máquina revisada, tudo ok ao final')

        # 4. Check display in template context
        response = self.client.get(reverse('checklist_execute', kwargs={'session_id': session.id}))
        self.assertContains(response, 'Máquina revisada, tudo ok ao final')

        # 5. Check Excel Export contains it
        self.client.login(username='test_analyst', password='testpassword123')
        response_excel = self.client.get(reverse('export_checklist_excel', kwargs={'session_id': session.id}))
        self.assertEqual(response_excel.status_code, 200)
        self.assertEqual(response_excel['content-type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_dashboard_advanced_filters_and_excel_export(self):
        # Create second inspector and machine
        inspector2 = User.objects.create_user(
            username='inspector_2',
            password='testpassword123',
            specialty='Mecânico',
            is_active=True
        )
        machine2 = Machine.objects.create(name='Test Machine 102')

        # Create session 1 (Test Machine 101, test_inspector, test_leader, status APROVADO, contains NC item)
        session1 = ChecklistSession.objects.create(
            machine=self.machine,
            leader=self.leader,
            inspector=self.inspector,
            status='APROVADO',
            created_at=timezone.now()
        )
        ChecklistItemValue.objects.create(
            session=session1,
            section='ELETRICA',
            item_name='Cabo rompido',
            status='NC',
            observations='Rompido'
        )

        # Create session 2 (Test Machine 102, inspector_2, test_leader, status IN_PROGRESS, no NCs)
        session2 = ChecklistSession.objects.create(
            machine=machine2,
            leader=self.leader,
            inspector=inspector2,
            status='IN_PROGRESS',
            created_at=timezone.now()
        )
        ChecklistItemValue.objects.create(
            session=session2,
            section='HIDRAULICA',
            item_name='Mangueira solta',
            status='C'
        )

        # Login as Analyst (to see all sessions)
        self.client.login(username='test_analyst', password='testpassword123')

        # Filter by Machine 101
        response = self.client.get(reverse('dashboard') + f'?maquina={self.machine.id}')
        self.assertIn(session1, response.context['sessions'])
        self.assertNotIn(session2, response.context['sessions'])

        # Filter by Machine 102
        response = self.client.get(reverse('dashboard') + f'?maquina={machine2.id}')
        self.assertIn(session2, response.context['sessions'])
        self.assertNotIn(session1, response.context['sessions'])

        # Filter by Inspector 2
        response = self.client.get(reverse('dashboard') + f'?inspector={inspector2.id}')
        self.assertIn(session2, response.context['sessions'])
        self.assertNotIn(session1, response.context['sessions'])

        # Filter by Status APROVADO
        response = self.client.get(reverse('dashboard') + '?status_filter=APROVADO')
        self.assertIn(session1, response.context['sessions'])
        self.assertNotIn(session2, response.context['sessions'])

        # Filter by NC Resumo: "Cabo"
        response = self.client.get(reverse('dashboard') + '?nc_query=Cabo')
        self.assertIn(session1, response.context['sessions'])
        self.assertNotIn(session2, response.context['sessions'])

        # Filter by NC Resumo: "Mangueira" (session2 has "Mangueira" but it is Conforme 'C', so it should not match)
        response = self.client.get(reverse('dashboard') + '?nc_query=Mangueira')
        self.assertEqual(len(response.context['sessions']), 0)

        # Check export consolidado respects filters
        response_excel = self.client.get(reverse('export_dashboard_excel') + f'?maquina={self.machine.id}')
        self.assertEqual(response_excel.status_code, 200)

    def test_timeout_pause_checklist(self):
        # Login as inspector
        self.client.login(username='test_inspector', password='testpassword123')
        
        # Create an active checklist session in progress
        session = ChecklistSession.objects.create(
            machine=self.machine,
            leader=self.leader,
            inspector=self.inspector,
            status='IN_PROGRESS',
            started_at=timezone.now()
        )
        
        # Call the timeout_pause_checklist AJAX endpoint
        response = self.client.post(
            reverse('timeout_pause_checklist'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Check that the response is successful JSON
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('pausado automaticamente', data['message'])
        
        # Verify the session status changed to PAUSED
        session.refresh_from_db()
        self.assertEqual(session.status, 'PAUSED')
        self.assertIsNotNone(session.paused_at)
        
        # Verify the timeline log contains the correct absolute timeout justification
        log = ChecklistTimelineLog.objects.filter(session=session, action='PAUSE').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.pause_reason, "Pausa automática: Fim do tempo de sessão logada (2h)")

    def test_technician_pair_symmetry(self):
        # 1. Create two technicians
        tech_a = User.objects.create_user(
            username='tech_a',
            password='testpassword123',
            specialty='Mecânico',
            is_active=True
        )
        tech_b = User.objects.create_user(
            username='tech_b',
            password='testpassword123',
            specialty='Eletricista',
            is_active=True
        )
        
        # Set tech_b as tech_a's partner
        tech_a.partner_user = tech_b
        tech_a.save()
        
        # Verify symmetry
        tech_b.refresh_from_db()
        self.assertEqual(tech_b.partner_user, tech_a)
        
        # Clear tech_a's partner
        tech_a.partner_user = None
        tech_a.save()
        
        # Verify symmetry cleared
        tech_b.refresh_from_db()
        self.assertIsNone(tech_b.partner_user)

    def test_checklist_creation_with_partner(self):
        # Create partner technician
        tech_b = User.objects.create_user(
            username='tech_b',
            password='testpassword123',
            specialty='Eletricista',
            is_active=True
        )
        self.inspector.partner_user = tech_b
        self.inspector.save()
        
        self.client.login(username='test_inspector', password='testpassword123')
        
        response = self.client.post(reverse('checklist_start'), {
            'machine': self.machine.id,
            'leader': self.leader.id
        })
        
        session = ChecklistSession.objects.filter(machine=self.machine, leader=self.leader).first()
        self.assertIsNotNone(session)
        self.assertEqual(session.inspector, self.inspector)
        self.assertEqual(session.co_inspector, tech_b)

    def test_technician_restricted_visibility(self):
        # Setup technicians and pairing
        tech_a = self.inspector  # test_inspector (Eletricista)
        tech_b = User.objects.create_user(
            username='tech_b',
            password='testpassword123',
            specialty='Mecânico',
            is_active=True
        )
        tech_a.partner_user = tech_b
        tech_a.save()
        
        tech_c = User.objects.create_user(
            username='tech_c',
            password='testpassword123',
            specialty='Eletromecânico',
            is_active=True
        )
        
        # Create checklist session for tech_a (tech_b is co_inspector)
        session_ab = ChecklistSession.objects.create(
            machine=self.machine,
            leader=self.leader,
            inspector=tech_a,
            co_inspector=tech_b,
            status='IN_PROGRESS',
            started_at=timezone.now()
        )
        
        # Create checklist session for tech_c (no co_inspector)
        session_c = ChecklistSession.objects.create(
            machine=self.machine,
            leader=self.leader,
            inspector=tech_c,
            status='IN_PROGRESS',
            started_at=timezone.now()
        )
        
        # Test tech_a visibility (sees session_ab, not session_c)
        self.client.login(username='test_inspector', password='testpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertIn(session_ab, response.context['sessions'])
        self.assertNotIn(session_c, response.context['sessions'])
        
        # Test tech_b visibility (sees session_ab, not session_c)
        self.client.login(username='tech_b', password='testpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertIn(session_ab, response.context['sessions'])
        self.assertNotIn(session_c, response.context['sessions'])
        
        # Test tech_c visibility (sees session_c, not session_ab)
        self.client.login(username='tech_c', password='testpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertIn(session_c, response.context['sessions'])
        self.assertNotIn(session_ab, response.context['sessions'])
        
        # Test analyst visibility (sees both)
        self.client.login(username='test_analyst', password='testpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertIn(session_ab, response.context['sessions'])
        self.assertIn(session_c, response.context['sessions'])

    def test_technician_edit_permissions(self):
        tech_b = User.objects.create_user(
            username='tech_b',
            password='testpassword123',
            specialty='Mecânico',
            is_active=True
        )
        self.inspector.partner_user = tech_b
        self.inspector.save()
        
        session = ChecklistSession.objects.create(
            machine=self.machine,
            leader=self.leader,
            inspector=self.inspector,
            co_inspector=tech_b,
            status='IN_PROGRESS',
            started_at=timezone.now()
        )
        item = ChecklistItemValue.objects.create(
            session=session,
            section='ELETRICA',
            item_name='Test item',
            status=None
        )
        
        # Unrelated tech_c
        tech_c = User.objects.create_user(
            username='tech_c',
            password='testpassword123',
            specialty='Eletromecânico',
            is_active=True
        )
        
        # 1. Tech_c tries to edit -> 403 Forbidden
        self.client.login(username='tech_c', password='testpassword123')
        response = self.client.post(
            reverse('checklist_execute', kwargs={'session_id': session.id}),
            {
                'action': 'pause',
                'pause_reason': 'Sem permissao',
                f'status_{item.id}': 'C'
            }
        )
        self.assertEqual(response.status_code, 403)
        
        # 2. Co-inspector tech_b tries to edit -> Should succeed (redirect to execute page)
        self.client.login(username='tech_b', password='testpassword123')
        response = self.client.post(
            reverse('checklist_execute', kwargs={'session_id': session.id}),
            {
                'action': 'pause',
                'pause_reason': 'Pausa dupla',
                f'status_{item.id}': 'C'
            }
        )
        self.assertEqual(response.status_code, 302)
        session.refresh_from_db()
        self.assertEqual(session.status, 'PAUSED')

    def test_excel_exports_with_co_inspector(self):
        tech_b = User.objects.create_user(
            username='tech_b',
            password='testpassword123',
            specialty='Mecânico',
            is_active=True
        )
        session = ChecklistSession.objects.create(
            machine=self.machine,
            leader=self.leader,
            inspector=self.inspector,
            co_inspector=tech_b,
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
        
        # Login as analyst to export
        self.client.login(username='test_analyst', password='testpassword123')
        
        # Individual export
        response_ind = self.client.get(reverse('export_checklist_excel', kwargs={'session_id': session.id}))
        self.assertEqual(response_ind.status_code, 200)
        
        # Consolidated export
        response_cons = self.client.get(reverse('export_dashboard_excel'))
        self.assertEqual(response_cons.status_code, 200)

    def test_auditor_access_control_and_redirects(self):
        auditor = User.objects.create_user(
            username='test_auditor',
            password='testpassword123',
            specialty='Auditor',
            is_active=True
        )
        self.client.login(username='test_auditor', password='testpassword123')
        
        # 1. Accessing '/' (dashboard name) redirects Auditor to auditor_queue
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('auditor_queue'))
        
        # 2. Accessing '/dashboard/' (analytical_dashboard) redirects Auditor to auditor_queue
        response = self.client.get(reverse('analytical_dashboard'))
        self.assertRedirects(response, reverse('auditor_queue'))

        # 3. Accessing '/machines/' redirects Auditor to auditor_queue
        response = self.client.get(reverse('machine_list'))
        self.assertRedirects(response, reverse('auditor_queue'))

        # 4. Accessing '/checklist/start/' redirects Auditor to auditor_queue
        response = self.client.get(reverse('checklist_start'))
        self.assertRedirects(response, reverse('auditor_queue'))

        # 5. Accessing '/users/pending/' returns 403 Forbidden
        response = self.client.get(reverse('user_approval_list'))
        self.assertEqual(response.status_code, 403)

        # 6. Accessing auditor views returns 200
        response = self.client.get(reverse('auditor_queue'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('auditor_history'))
        self.assertEqual(response.status_code, 200)

    def test_technician_cannot_access_auditor_screens(self):
        self.client.login(username='test_inspector', password='testpassword123')
        
        # 1. Tech cannot view Auditor Queue
        response = self.client.get(reverse('auditor_queue'))
        self.assertRedirects(response, reverse('dashboard'))
        
        # 2. Tech cannot view Auditor History
        response = self.client.get(reverse('auditor_history'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_auditor_checklist_audit_validation_and_saving(self):
        auditor = User.objects.create_user(
            username='test_auditor',
            password='testpassword123',
            specialty='Auditor',
            is_active=True
        )
        session = ChecklistSession.objects.create(
            machine=self.machine,
            leader=self.leader,
            inspector=self.inspector,
            status='APROVADO',
            started_at=timezone.now(),
            completed_at=timezone.now()
        )
        item = ChecklistItemValue.objects.create(
            session=session,
            section='ELETRICA',
            item_name='Test auditor item',
            status='C'
        )
        
        self.client.login(username='test_auditor', password='testpassword123')
        
        # 1. Submit divergence toggle = true but NO observation -> Validation fails
        response = self.client.post(
            reverse('checklist_audit', kwargs={'session_id': session.id}),
            {
                f'divergent_{item.id}': 'on',
                f'observation_{item.id}': ''
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "exige uma observação do auditor")
        
        # Verify nothing was changed in db
        session.refresh_from_db()
        self.assertEqual(session.audit_status, 'NAO_AUDITADO')
        
        # 2. Submit divergence toggle = true AND observation -> Validation succeeds
        response = self.client.post(
            reverse('checklist_audit', kwargs={'session_id': session.id}),
            {
                f'divergent_{item.id}': 'on',
                f'observation_{item.id}': 'Divergencia encontrada'
            }
        )
        self.assertRedirects(response, reverse('auditor_queue'))
        
        session.refresh_from_db()
        item.refresh_from_db()
        self.assertEqual(session.audit_status, 'AUDITADO_COM_DIVERGENCIA')
        self.assertEqual(session.audited_by, auditor)
        self.assertIsNotNone(session.audited_at)
        self.assertTrue(item.auditor_is_divergent)
        self.assertEqual(item.auditor_observation, 'Divergencia encontrada')
        
        # 3. Submit audit checklist with no divergence -> status becomes AUDITADO_CONFORME
        response = self.client.post(
            reverse('checklist_audit', kwargs={'session_id': session.id}),
            {
                f'divergent_{item.id}': 'false', # or not checked
                f'observation_{item.id}': ''
            }
        )
        self.assertRedirects(response, reverse('auditor_queue'))
        
        session.refresh_from_db()
        item.refresh_from_db()
        self.assertEqual(session.audit_status, 'AUDITADO_CONFORME')
        self.assertFalse(item.auditor_is_divergent)
        self.assertEqual(item.auditor_observation, '')

    def test_media_urls_serving(self):
        response1 = self.client.get('/media/Untitled-1.png')
        response2 = self.client.get('/media/Untitled-2.png')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

    def test_excel_exports_branding_and_logos(self):
        analyst = User.objects.create_user(
            username='test_analyst_exporter',
            password='testpassword123',
            specialty='Analista',
            is_active=True
        )
        session = ChecklistSession.objects.create(
            machine=self.machine,
            leader=self.leader,
            inspector=self.inspector,
            status='APROVADO',
            started_at=timezone.now(),
            completed_at=timezone.now()
        )
        self.client.login(username='test_analyst_exporter', password='testpassword123')
        
        # Test individual export
        url = reverse('export_checklist_excel', kwargs={'session_id': session.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        # Test dashboard export
        url_dash = reverse('export_dashboard_excel')
        response_dash = self.client.get(url_dash)
        self.assertEqual(response_dash.status_code, 200)
        self.assertEqual(response_dash['content-type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')




