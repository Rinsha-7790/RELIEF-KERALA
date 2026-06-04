import os

templates = {
'templates/transparency/home.html': """{% extends 'base.html' %}
{% block title %}Home - Disaster Relief Kerala{% endblock %}
{% block content %}
<div class="hero text-center">
  <div class="container">
    <h1 class="display-4 fw-bold">🆘 Disaster Relief Kerala</h1>
    <p class="lead mb-4">Connecting donors, volunteers and relief camps transparently</p>
    <a href="{% url 'money_donate' %}" class="btn btn-light btn-lg me-3">💰 Donate Now</a>
    <a href="{% url 'volunteer_register' %}" class="btn btn-outline-light btn-lg">🙋 Volunteer</a>
  </div>
</div>
<div class="container mt-5">
  <div class="row text-center g-4">
    <div class="col-md-4">
      <div class="card p-4">
        <h2 class="text-danger fw-bold">₹{{ total_money }}</h2>
        <p class="text-muted mb-0">Total Funds Raised</p>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card p-4">
        <h2 class="text-danger fw-bold">{{ total_camps }}</h2>
        <p class="text-muted mb-0">Active Relief Camps</p>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card p-4">
        <h2 class="text-danger fw-bold">{{ total_volunteers }}</h2>
        <p class="text-muted mb-0">Active Volunteers</p>
      </div>
    </div>
  </div>
</div>
{% if urgent_needs %}
<div class="container mt-5">
  <h3 class="fw-bold mb-4">🔴 Urgent Needs</h3>
  <div class="row g-3">
    {% for need in urgent_needs %}
    <div class="col-md-4">
      <div class="card p-3 border-danger">
        <h5 class="text-danger">{{ need.item }}</h5>
        <p class="mb-1">Camp: <strong>{{ need.camp.name }}</strong></p>
        <p class="mb-1">Needed: <strong>{{ need.quantity_needed }} {{ need.unit }}</strong></p>
        <div class="progress mt-2">
          <div class="progress-bar bg-danger" style="width: {{ need.percent_fulfilled }}%"></div>
        </div>
      </div>
    </div>
    {% endfor %}
  </div>
</div>
{% endif %}
<div class="container mt-5">
  <h3 class="fw-bold mb-4">🏕️ Active Relief Camps</h3>
  <div class="row g-4">
    {% for camp in camps %}
    <div class="col-md-4">
      <div class="card p-4">
        <h5 class="fw-bold">{{ camp.name }}</h5>
        <p class="text-muted mb-1">📍 {{ camp.location }}</p>
        <p class="mb-1">👥 {{ camp.people_count }} people</p>
        <p class="mb-3">📞 {{ camp.contact_person }}</p>
        <a href="{% url 'camp_detail' camp.pk %}" class="btn btn-donate w-100">View Needs</a>
      </div>
    </div>
    {% empty %}
    <div class="col-12"><div class="alert alert-info">No active camps at the moment.</div></div>
    {% endfor %}
  </div>
</div>
<div class="container mt-5 mb-5">
  <div class="row g-4">
    <div class="col-md-4">
      <div class="card p-4 text-center">
        <div style="font-size:3rem">💰</div>
        <h5 class="mt-3">Donate Money</h5>
        <p class="text-muted">Send funds directly to verified relief camps</p>
        <a href="{% url 'money_donate' %}" class="btn btn-donate">Donate Now</a>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card p-4 text-center">
        <div style="font-size:3rem">📦</div>
        <h5 class="mt-3">Donate Items</h5>
        <p class="text-muted">Food, medicine, clothes and other essentials</p>
        <a href="{% url 'item_donate' %}" class="btn btn-donate">Donate Items</a>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card p-4 text-center">
        <div style="font-size:3rem">🙋</div>
        <h5 class="mt-3">Volunteer</h5>
        <p class="text-muted">Register your skills and help on the ground</p>
        <a href="{% url 'volunteer_register' %}" class="btn btn-donate">Register</a>
      </div>
    </div>
  </div>
</div>
{% endblock %}""",

'templates/accounts/login.html': """{% extends 'base.html' %}
{% block title %}Login{% endblock %}
{% block content %}
<div class="container mt-5">
  <div class="row justify-content-center">
    <div class="col-md-5">
      <div class="card p-4">
        <h3 class="text-center fw-bold mb-4">🔐 Login</h3>
        <form method="POST">
          {% csrf_token %}
          {% for field in form %}
          <div class="mb-3">
            <label class="form-label fw-semibold">{{ field.label }}</label>
            <input type="{{ field.field.widget.input_type }}" name="{{ field.html_name }}" class="form-control" placeholder="{{ field.label }}">
          </div>
          {% endfor %}
          <button type="submit" class="btn btn-donate w-100 mt-2">Login</button>
        </form>
        <p class="text-center mt-3">Don't have an account? <a href="{% url 'register' %}">Register here</a></p>
      </div>
    </div>
  </div>
</div>
{% endblock %}""",

'templates/accounts/register.html': """{% extends 'base.html' %}
{% block title %}Register{% endblock %}
{% block content %}
<div class="container mt-5">
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card p-4">
        <h3 class="text-center fw-bold mb-4">📝 Create Account</h3>
        <form method="POST">
          {% csrf_token %}
          {% for field in form %}
          <div class="mb-3">
            <label class="form-label fw-semibold">{{ field.label }}</label>
            {{ field }}
            {% if field.errors %}<div class="text-danger small">{{ field.errors }}</div>{% endif %}
          </div>
          {% endfor %}
          <button type="submit" class="btn btn-donate w-100 mt-2">Create Account</button>
        </form>
        <p class="text-center mt-3">Already have an account? <a href="{% url 'login' %}">Login here</a></p>
      </div>
    </div>
  </div>
</div>
{% endblock %}""",

'templates/camps/camp_list.html': """{% extends 'base.html' %}
{% block title %}Relief Camps{% endblock %}
{% block content %}
<div class="container mt-5">
  <h2 class="fw-bold mb-4">🏕️ Active Relief Camps</h2>
  <div class="row g-4">
    {% for camp in camps %}
    <div class="col-md-4">
      <div class="card p-4 h-100">
        <h5 class="fw-bold">{{ camp.name }}</h5>
        <p class="text-muted mb-1">📍 {{ camp.location }}</p>
        <p class="mb-1">🏛️ {{ camp.district }}</p>
        <p class="mb-1">👥 {{ camp.people_count }} people</p>
        <p class="mb-3">📞 {{ camp.contact_person }}</p>
        <a href="{% url 'camp_detail' camp.pk %}" class="btn btn-donate mt-auto">View Needs →</a>
      </div>
    </div>
    {% empty %}
    <div class="col-12"><div class="alert alert-info">No active camps right now.</div></div>
    {% endfor %}
  </div>
</div>
{% endblock %}""",

'templates/camps/camp_detail.html': """{% extends 'base.html' %}
{% block title %}{{ camp.name }}{% endblock %}
{% block content %}
<div class="container mt-5">
  <div class="card p-4 mb-4">
    <h2 class="fw-bold">🏕️ {{ camp.name }}</h2>
    <p class="text-muted">📍 {{ camp.location }}, {{ camp.district }}</p>
    <div class="row">
      <div class="col-md-4"><strong>👥 People:</strong> {{ camp.people_count }}</div>
      <div class="col-md-4"><strong>📞 Contact:</strong> {{ camp.contact_person }}</div>
      <div class="col-md-4"><strong>📱 Phone:</strong> {{ camp.contact_phone }}</div>
    </div>
  </div>
  <h4 class="fw-bold mb-3">📋 Current Needs</h4>
  <div class="row g-3">
    {% for need in needs %}
    <div class="col-md-4">
      <div class="card p-3 {% if need.priority == 'urgent' %}border-danger{% endif %}">
        <div class="d-flex justify-content-between">
          <h6 class="fw-bold">{{ need.item }}</h6>
          <span class="badge {% if need.priority == 'urgent' %}bg-danger{% elif need.priority == 'normal' %}bg-warning{% else %}bg-success{% endif %}">{{ need.get_priority_display }}</span>
        </div>
        <p class="mb-1 small">Needed: {{ need.quantity_needed }} {{ need.unit }}</p>
        <p class="mb-2 small">Received: {{ need.quantity_received }} {{ need.unit }}</p>
        <div class="progress" style="height:8px">
          <div class="progress-bar bg-success" style="width:{{ need.percent_fulfilled }}%"></div>
        </div>
        <small class="text-muted">{{ need.percent_fulfilled }}% fulfilled</small>
      </div>
    </div>
    {% empty %}
    <div class="col-12"><div class="alert alert-success">✅ No pending needs!</div></div>
    {% endfor %}
  </div>
  <div class="mt-4">
    <a href="{% url 'item_donate' %}" class="btn btn-donate me-2">📦 Donate Items</a>
    <a href="{% url 'money_donate' %}" class="btn btn-donate">💰 Donate Money</a>
  </div>
</div>
{% endblock %}""",

'templates/donations/money_donate.html': """{% extends 'base.html' %}
{% block title %}Donate Money{% endblock %}
{% block content %}
<div class="container mt-5">
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card p-4">
        <h3 class="fw-bold mb-4 text-center">💰 Donate Money</h3>
        <form method="POST">
          {% csrf_token %}
          <div class="mb-3">
            <label class="form-label fw-semibold">Your Name</label>
            <input type="text" name="donor_name" class="form-control" required>
          </div>
          <div class="mb-3">
            <label class="form-label fw-semibold">Amount (₹)</label>
            <input type="number" name="amount" class="form-control" min="1" required>
          </div>
          <div class="mb-3">
            <label class="form-label fw-semibold">Select Camp (optional)</label>
            <select name="camp" class="form-select">
              <option value="">-- General Fund --</option>
              {% for camp in camps %}
              <option value="{{ camp.pk }}">{{ camp.name }} - {{ camp.district }}</option>
              {% endfor %}
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label fw-semibold">Purpose (optional)</label>
            <input type="text" name="purpose" class="form-control" placeholder="e.g. Food, Medicine">
          </div>
          <button type="submit" class="btn btn-donate w-100">💰 Donate Now</button>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}""",

'templates/donations/item_donate.html': """{% extends 'base.html' %}
{% block title %}Donate Items{% endblock %}
{% block content %}
<div class="container mt-5">
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card p-4">
        <h3 class="fw-bold mb-4 text-center">📦 Donate Items</h3>
        <form method="POST">
          {% csrf_token %}
          <div class="mb-3">
            <label class="form-label fw-semibold">Your Name</label>
            <input type="text" name="donor_name" class="form-control" required>
          </div>
          <div class="mb-3">
            <label class="form-label fw-semibold">Your Phone</label>
            <input type="text" name="donor_phone" class="form-control" required>
          </div>
          <div class="mb-3">
            <label class="form-label fw-semibold">Item Name</label>
            <input type="text" name="item_name" class="form-control" placeholder="e.g. Rice, Blankets" required>
          </div>
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label fw-semibold">Quantity</label>
              <input type="number" name="quantity" class="form-control" min="1" required>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label fw-semibold">Unit</label>
              <select name="unit" class="form-select">
                <option value="kg">kg</option>
                <option value="packets">packets</option>
                <option value="pieces">pieces</option>
                <option value="boxes">boxes</option>
                <option value="litres">litres</option>
              </select>
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label fw-semibold">Send to Camp</label>
            <select name="camp" class="form-select">
              <option value="">-- Select Camp --</option>
              {% for camp in camps %}
              <option value="{{ camp.pk }}">{{ camp.name }} - {{ camp.district }}</option>
              {% endfor %}
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label fw-semibold">Notes (optional)</label>
            <textarea name="notes" class="form-control" rows="2"></textarea>
          </div>
          <button type="submit" class="btn btn-donate w-100">📦 Submit Donation</button>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}""",

'templates/donations/success.html': """{% extends 'base.html' %}
{% block title %}Thank You!{% endblock %}
{% block content %}
<div class="container mt-5 text-center">
  <div class="card p-5" style="max-width:500px;margin:auto">
    <div style="font-size:5rem">🙏</div>
    <h2 class="fw-bold mt-3">Thank You!</h2>
    <p class="text-muted">Your donation has been recorded. Every contribution makes a difference.</p>
    <a href="{% url 'dashboard' %}" class="btn btn-donate me-2">View Transparency Dashboard</a>
    <a href="{% url 'home' %}" class="btn btn-outline-secondary mt-2">Back to Home</a>
  </div>
</div>
{% endblock %}""",

'templates/volunteers/register.html': """{% extends 'base.html' %}
{% block title %}Volunteer Registration{% endblock %}
{% block content %}
<div class="container mt-5">
  <div class="row justify-content-center">
    <div class="col-md-6">
      <div class="card p-4">
        <h3 class="fw-bold mb-4 text-center">🙋 Volunteer Registration</h3>
        <form method="POST">
          {% csrf_token %}
          <div class="mb-3">
            <label class="form-label fw-semibold">Your Skills</label>
            <input type="text" name="skills" class="form-control" placeholder="e.g. First Aid, Cooking, Driving" required>
          </div>
          <div class="mb-3">
            <label class="form-label fw-semibold">Your Location</label>
            <input type="text" name="location" class="form-control" placeholder="e.g. Kozhikode" required>
          </div>
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label fw-semibold">Available From</label>
              <input type="date" name="available_from" class="form-control" required>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label fw-semibold">Available Until</label>
              <input type="date" name="available_until" class="form-control" required>
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label fw-semibold">Aadhaar / ID Number</label>
            <input type="text" name="id_proof_number" class="form-control" required>
          </div>
          <button type="submit" class="btn btn-donate w-100">Submit Registration</button>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}""",

'templates/volunteers/success.html': """{% extends 'base.html' %}
{% block title %}Registration Submitted{% endblock %}
{% block content %}
<div class="container mt-5 text-center">
  <div class="card p-5" style="max-width:500px;margin:auto">
    <div style="font-size:5rem">✅</div>
    <h2 class="fw-bold mt-3">Registration Submitted!</h2>
    <p class="text-muted">Your volunteer registration is under review. Admin will approve it shortly.</p>
    <a href="{% url 'home' %}" class="btn btn-donate">Back to Home</a>
  </div>
</div>
{% endblock %}""",

'templates/transparency/dashboard.html': """{% extends 'base.html' %}
{% block title %}Transparency Dashboard{% endblock %}
{% block content %}
<div class="container mt-5">
  <h2 class="fw-bold mb-4">📊 Transparency Dashboard</h2>
  <div class="row g-4 mb-5">
    <div class="col-md-4">
      <div class="card p-4 text-center">
        <h3 class="text-success fw-bold">₹{{ total_money }}</h3>
        <p class="text-muted mb-0">Total Funds Received</p>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card p-4 text-center">
        <h3 class="text-warning fw-bold">₹{{ allocated }}</h3>
        <p class="text-muted mb-0">Allocated to Camps</p>
      </div>
    </div>
    <div class="col-md-4">
      <div class="card p-4 text-center">
        <h3 class="text-danger fw-bold">₹{{ unallocated }}</h3>
        <p class="text-muted mb-0">Unallocated Funds</p>
      </div>
    </div>
  </div>
  <h4 class="fw-bold mb-3">💰 Recent Money Donations</h4>
  <div class="card mb-5">
    <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead class="table-dark">
          <tr><th>Donor</th><th>Amount</th><th>Camp</th><th>Status</th><th>Date</th></tr>
        </thead>
        <tbody>
          {% for d in money_donations %}
          <tr>
            <td>{{ d.donor_name }}</td>
            <td>₹{{ d.amount }}</td>
            <td>{{ d.camp.name|default:"General Fund" }}</td>
            <td><span class="badge bg-success">{{ d.get_status_display }}</span></td>
            <td>{{ d.date|date:"d M Y" }}</td>
          </tr>
          {% empty %}
          <tr><td colspan="5" class="text-center text-muted">No donations yet</td></tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
  <h4 class="fw-bold mb-3">📦 Recent Item Donations</h4>
  <div class="card">
    <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead class="table-dark">
          <tr><th>Donor</th><th>Item</th><th>Qty</th><th>Camp</th><th>Status</th><th>Date</th></tr>
        </thead>
        <tbody>
          {% for d in item_donations %}
          <tr>
            <td>{{ d.donor_name }}</td>
            <td>{{ d.item_name }}</td>
            <td>{{ d.quantity }} {{ d.unit }}</td>
            <td>{{ d.camp.name|default:"-" }}</td>
            <td><span class="badge bg-info">{{ d.get_status_display }}</span></td>
            <td>{{ d.date|date:"d M Y" }}</td>
          </tr>
          {% empty %}
          <tr><td colspan="6" class="text-center text-muted">No item donations yet</td></tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>
{% endblock %}""",
}

for path, content in templates.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Written: {path}')

print('\n✅ All templates written successfully!')