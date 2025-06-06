from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Ticket, db
from app.forms import LoginForm, RegisterForm
from wtforms import SelectField, TextAreaField
from flask_wtf import FlaskForm
from wtforms import SubmitField
from datetime import datetime
import io
import pyotp
from app.forms import ChangePasswordForm

class AssignTicketForm(FlaskForm):
    ticket_id = SelectField('Ticket', coerce=int)
    user_id = SelectField('Asignar a', coerce=int)
    submit = SubmitField('Asignar')

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            # MFA activado pero no configurado aún
            if user.mfa_enabled and not user.mfa_confirmed:
                login_user(user)
                return redirect(url_for('main.confirm_mfa'))

            # MFA activado y confirmado
            if user.mfa_enabled:
                if not form.mfa_code.data:
                    flash('Se requiere el código MFA.', 'danger')
                    return render_template('login.html', form=form)
                elif not user.verify_totp(form.mfa_code.data):
                    flash('Código MFA incorrecto.', 'danger')
                    return render_template('login.html', form=form)

            # Login exitoso
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('main.dashboard'))

        flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('login.html', form=form)


    




@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, role='usuario')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registro exitoso. Ahora puedes iniciar sesión.')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        users = User.query.all()
        return render_template('admin_dashboard.html', users=users)
    elif current_user.role == 'manager':
        tickets = Ticket.query.all()
        return render_template('manager_dashboard.html', tickets=tickets)
    else:
        tickets = Ticket.query.filter_by(assigned_to=current_user).all()
        return render_template('user_dashboard.html', tickets=tickets)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/assign_ticket', methods=['GET', 'POST'])
@login_required
def assign_ticket():
    if current_user.role != 'manager':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    form = AssignTicketForm()
    form.ticket_id.choices = [(t.id, t.title) for t in Ticket.query.filter_by(assigned_to=None).all()]
    form.user_id.choices = [(u.id, u.username) for u in User.query.filter_by(role='usuario').all()]

    if form.validate_on_submit():
        ticket = Ticket.query.get(form.ticket_id.data)
        user = User.query.get(form.user_id.data)
        ticket.assigned_to = user
        db.session.commit()
        flash(f'Ticket "{ticket.title}" asignado a {user.username}')
        return redirect(url_for('main.dashboard'))

    return render_template('assign_ticket.html', form=form)

@main.route('/admin/edit_user/<int:user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    new_role = request.form.get('role')
    user = User.query.get(user_id)
    if user and new_role in ['admin', 'manager', 'usuario'] and new_role != user.role:
        from app.models import RoleChangeHistory
        change = RoleChangeHistory(
            user_id=user.id,
            changed_by_id=current_user.id,
            old_role=user.role,
            new_role=new_role
        )
        user.role = new_role
        db.session.add(change)
        db.session.commit()
        flash(f'Rol de {user.username} actualizado a {new_role}')
    return redirect(url_for('main.dashboard'))

@main.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f'Usuario {user.username} eliminado correctamente')
    return redirect(url_for('main.dashboard'))

@main.route('/update_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    # Solo el usuario asignado puede cambiar el estado
    if ticket.assigned_to != current_user:
        flash('No tienes permiso para modificar este ticket.')
        return redirect(url_for('main.dashboard'))

    new_status = request.form.get('status')
    if new_status and new_status != ticket.status:
        from app.models import TicketHistory
        history = TicketHistory(
            ticket_id=ticket.id,
            old_status=ticket.status,
            new_status=new_status,
            changed_by_id=current_user.id
        )
        ticket.status = new_status
        db.session.add(history)
        db.session.commit()
        flash('Estado del ticket actualizado.')

    return redirect(url_for('main.dashboard'))

@main.route('/ticket_history')
@login_required
def ticket_history():
    if current_user.role not in ['admin', 'manager']:
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    from app.models import TicketHistory, Ticket, User
    ticket_id = request.args.get('ticket_id', type=int)
    user_id = request.args.get('user_id', type=int)

    history_query = TicketHistory.query
    if ticket_id:
        history_query = history_query.filter_by(ticket_id=ticket_id)
    if user_id:
        history_query = history_query.filter_by(changed_by_id=user_id)

    history_entries = history_query.order_by(TicketHistory.timestamp.desc()).all()
    tickets = Ticket.query.all()
    users = User.query.all()

    return render_template('ticket_history.html', history=history_entries, tickets=tickets, users=users, selected_ticket=ticket_id, selected_user=user_id)

@main.route('/role_history')
@login_required
def role_history():
    if current_user.role != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    from app.models import RoleChangeHistory
    history = RoleChangeHistory.query.order_by(RoleChangeHistory.timestamp.desc()).all()
    return render_template('role_history.html', history=history)

import csv
from flask import make_response

@main.route('/export/ticket_history.csv')
@login_required
def export_ticket_history():
    if current_user.role not in ['admin', 'manager']:
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    from app.models import TicketHistory
    history = TicketHistory.query.order_by(TicketHistory.timestamp.desc()).all()

    output_stream = io.StringIO()
    writer = csv.writer(output_stream)
    writer.writerow(['Fecha', 'Ticket', 'De', 'A', 'Modificado por'])

    for h in history:
        writer.writerow([
            h.timestamp.strftime('%Y-%m-%d %H:%M'),
            h.ticket.title,
            h.old_status,
            h.new_status,
            h.changed_by.username
        ])

    response = make_response(output_stream.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=ticket_history.csv'
    response.headers['Content-type'] = 'text/csv; charset=utf-8'
    return response

@main.route('/export/role_history.csv')
@login_required
def export_role_history():
    if current_user.role != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    from app.models import RoleChangeHistory
    history = RoleChangeHistory.query.order_by(RoleChangeHistory.timestamp.desc()).all()

    output_stream = io.StringIO()
    writer = csv.writer(output_stream)
    writer.writerow(['Fecha', 'Usuario', 'De', 'A', 'Cambiado por'])
    for h in history:
        writer.writerow([
            h.timestamp.strftime('%Y-%m-%d %H:%M'),
            h.user.username if h.user else '(eliminado)',
            h.old_role,
            h.new_role,
            h.changed_by.username if h.changed_by else '(eliminado)'
        ])

    response = make_response(output_stream.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=role_history.csv'
    response.headers['Content-type'] = 'text/csv; charset=utf-8'
    return response

from fpdf import FPDF
from flask import make_response

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Historial de Cambios de Tickets", 0, 1, "C")
        self.ln(5)

    def add_entry(self, timestamp, ticket_title, old_status, new_status, changed_by):
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 10, f"{timestamp} - {ticket_title}: {old_status} -> {new_status} (por {changed_by})")
        self.ln(1)


@main.route('/export/ticket_history.pdf')
@login_required
def export_ticket_history_pdf():
    if current_user.role not in ['admin', 'manager']:
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    from app.models import TicketHistory
    history = TicketHistory.query.order_by(TicketHistory.timestamp.desc()).all()

    pdf = PDF()
    pdf.add_page()

    for h in history:
        pdf.add_entry(
            h.timestamp.strftime('%Y-%m-%d %H:%M'),
            h.ticket.title,
            h.old_status,
            h.new_status,
            h.changed_by.username
        )

    output = pdf.output(dest='S').encode('latin1')
    response = make_response(output)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=ticket_history.pdf'
    return response

class RolePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Historial de Cambios de Roles", 0, 1, "C")
        self.ln(5)

    def add_entry(self, timestamp, username, old_role, new_role, changed_by):
        self.set_font("Arial", "", 10)
        # Solo una línea por entrada para evitar saltos raros
        line = f"{timestamp} - {username}: {old_role} -> {new_role} (por {changed_by})"
        self.cell(0, 10, line, ln=True)

        
@main.route('/export/role_history.pdf')
@login_required
def export_role_history_pdf():
    if current_user.role != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    from app.models import RoleChangeHistory
    history = RoleChangeHistory.query.order_by(RoleChangeHistory.timestamp.desc()).all()

    pdf = RolePDF()
    pdf.add_page()

    for h in history:
        username = h.user.username if h.user else '(eliminado)'
        changed_by = h.changed_by.username if h.changed_by else '(eliminado)'

        pdf.add_entry(
            h.timestamp.strftime('%Y-%m-%d %H:%M'),
            username,
            h.old_role,
            h.new_role,
            changed_by
        )

    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=role_history.pdf'
    return response

@main.route('/create_ticket', methods=['GET', 'POST'])
@login_required
def create_ticket():
    if current_user.role != 'manager':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    from app.forms import CreateTicketForm
    form = CreateTicketForm()

    if form.validate_on_submit():
        ticket = Ticket(
            title=form.title.data,
            description=form.description.data,
            status='pendiente'
        )
        db.session.add(ticket)
        db.session.commit()

        # Registrar en el historial como creación
        from app.models import TicketHistory
        history = TicketHistory(
            ticket_id=ticket.id,
            old_status='-',
            new_status='pendiente',
            changed_by_id=current_user.id
        )
        db.session.add(history)
        db.session.commit()

        flash('Ticket creado correctamente.')
        return redirect(url_for('main.dashboard'))

    return render_template('create_ticket.html', form=form)

@main.route('/export/created_tickets.pdf')
@login_required
def export_created_tickets_pdf():
    if current_user.role != 'manager':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    tickets = Ticket.query.order_by(Ticket.id.desc()).all()

    pdf = PDF()
    pdf.add_page()

    for ticket in tickets:
        if ticket.assigned_to is None:
            pdf.add_entry(
                timestamp="(sin fecha)",
                ticket_title=ticket.title,
                old_status='-',
                new_status=ticket.status,
                changed_by=current_user.username
            )

    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=created_tickets.pdf'
    return response

@main.route('/export/created_tickets.csv')
@login_required
def export_created_tickets_csv():
    if current_user.role != 'manager':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    tickets = Ticket.query.filter_by(assigned_to=None).order_by(Ticket.id.desc()).all()

    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Título', 'Descripción', 'Estado'])
    for t in tickets:
        writer.writerow([t.id, t.title, t.description, t.status])

    output = make_response(si.getvalue())
    output.headers['Content-Disposition'] = 'attachment; filename=created_tickets.csv'
    output.headers['Content-type'] = 'text/csv; charset=utf-8'
    return output

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@main.route('/admin/activate_mfa/<int:user_id>')
@login_required
def activate_mfa(user_id):
    if current_user.role != 'admin':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('main.dashboard'))

    user = User.query.get_or_404(user_id)

    if not user.mfa_secret:
        user.mfa_secret = pyotp.random_base32()
    user.mfa_enabled = True
    db.session.commit()

    import qrcode
    import io
    import base64

    uri = user.get_totp_uri()
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template('show_mfa_qr.html', username=user.username, qr_data=img_b64)

@main.route('/admin/deactivate_mfa/<int:user_id>')
@login_required
def deactivate_mfa(user_id):
    if current_user.role != 'admin':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('main.dashboard'))

    user = User.query.get_or_404(user_id)

    user.mfa_enabled = False
    user.mfa_secret = None
    db.session.commit()

    flash(f'MFA desactivado para {user.username}.', 'info')
    return redirect(url_for('main.dashboard'))

@main.route('/confirm_mfa', methods=['GET', 'POST'])
@login_required
def confirm_mfa():
    import pyotp, qrcode, base64

    # Asegurarse de que MFA esté activado pero no confirmado
    if not current_user.mfa_enabled or current_user.mfa_confirmed:
        return redirect(url_for('main.dashboard'))

    # Generar código QR si no tiene secreto
    if not current_user.mfa_secret:
        current_user.mfa_secret = pyotp.random_base32()
        db.session.commit()

    uri = current_user.get_totp_uri()
    qr = qrcode.make(uri)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    if request.method == 'POST':
        token = request.form.get('token')
        if current_user.verify_totp(token):
            current_user.mfa_confirmed = True
            db.session.commit()
            flash('✅ MFA configurado correctamente.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('❌ Código incorrecto. Inténtalo de nuevo.', 'danger')

    return render_template('confirm_mfa.html', qr_b64=qr_b64)


@main.route('/cambiar_contrasena', methods=['GET', 'POST'])
@login_required
def cambiar_contrasena():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Contraseña actual incorrecta', 'danger')
        else:
            current_user.set_password(form.new_password.data)
            from app import db
            db.session.commit()
            flash('Contraseña cambiada correctamente', 'success')
            return redirect(url_for('main.dashboard'))
    return render_template('cambiar_contrasena.html', form=form)


