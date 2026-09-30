// ============================================================
// LabReserve Application Client Logic (Role-Based & Live SQLite)
// ============================================================

const API_BASE = "/api";

// Application State
const state = {
  currentUser: {
    id: 1,
    name: "Admin User",
    role: "Administrator",
    eId: "ADMIN001",
    department: "Computer Science"
  },
  currentScreen: "dashboard",
  currentBookingTab: "all",
  laboratories: [],
  users: [],
  equipment: [],
  bookings: [],
  currentWeekIndex: 0
};

// Screen headers mapping
const SCREEN_TITLES = {
  dashboard: {
    title: "Dashboard",
    subtitle: "Overview of laboratory operations and reservations"
  },
  users: {
    title: "User Management",
    subtitle: "Manage laboratory users and access permissions"
  },
  laboratories: {
    title: "Laboratory Management",
    subtitle: "Manage university laboratories and their configurations"
  },
  availability: {
    title: "Laboratory Availability",
    subtitle: "View and schedule laboratory calendar blocks"
  },
  bookings: {
    title: "Bookings",
    subtitle: "View and manage laboratory reservations"
  },
  equipment: {
    title: "Equipment Management",
    subtitle: "Track and manage laboratory scientific equipment"
  },
  settings: {
    title: "Settings",
    subtitle: "Configure system preferences and double-booking rules"
  }
};

// Initialize App
document.addEventListener("DOMContentLoaded", () => {
  const today = new Date().toISOString().split('T')[0];
  const dateInput = document.getElementById("new-booking-date");
  if (dateInput) dateInput.value = today;

  const savedUser = localStorage.getItem("labreserve_user");
  if (savedUser) {
    try {
      state.currentUser = JSON.parse(savedUser);
      showAppShell();
    } catch (e) {
      // stay on login
    }
  }
});

// ============================================================
// AUTHENTICATION & LOGIN
// ============================================================
function fillLogin(eId, pass) {
  document.getElementById("login-id").value = eId;
  document.getElementById("login-password").value = pass;
}

function togglePasswordVisibility(id) {
  const input = document.getElementById(id);
  input.type = input.type === "password" ? "text" : "password";
}

async function handleLoginSubmit(event) {
  event.preventDefault();
  const eId = document.getElementById("login-id").value.trim();
  const password = document.getElementById("login-password").value.trim();

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ e_id: eId, password: password })
    });
    const data = await res.json();

    if (data.success) {
      const u = data.user;
      let initials = "U";
      if (u.name) {
        const parts = u.name.split(" ");
        initials = parts.length > 1 ? (parts[0][0] + parts[1][0]).toUpperCase() : parts[0].slice(0, 2).toUpperCase();
      }

      state.currentUser = {
        id: u.user_id,
        name: u.name,
        role: u.role_name || "Administrator",
        initials: initials,
        eId: u.e_id,
        department: u.department || ""
      };

      if (document.getElementById("login-remember").checked) {
        localStorage.setItem("labreserve_user", JSON.stringify(state.currentUser));
      }

      showToast(`Welcome back, ${state.currentUser.name}!`);
      showAppShell();
    } else {
      showToast(data.message || "Invalid credentials", true);
    }
  } catch (err) {
    showToast("Server communication error. Please try again.", true);
  }
}

function showAppShell() {
  document.getElementById("view-login").style.display = "none";
  document.getElementById("view-app").style.display = "flex";

  updateUserWidget();
  applyRolePermissions();
  loadAllData();
  switchScreen("dashboard");
}

function handleLogout() {
  localStorage.removeItem("labreserve_user");
  document.getElementById("view-app").style.display = "none";
  document.getElementById("view-login").style.display = "flex";
  showToast("Successfully signed out.");
}

function updateUserWidget() {
  const u = state.currentUser;

  // Header chip
  document.getElementById("header-user-badge").innerText = u.name;
  const roleBadge = document.getElementById("header-role-badge");
  roleBadge.innerText = u.role;
  
  const avatar = document.getElementById("header-avatar");
  if (avatar) avatar.innerText = u.initials || u.name.slice(0, 2).toUpperCase();
  if (u.role === "Administrator") {
    roleBadge.style.color = "#2563eb";
  } else if (u.role === "Faculty" || u.role === "Lecturer") {
    roleBadge.style.color = "#0f766e";
  } else if (u.role === "Lab Technician") {
    roleBadge.style.color = "#7e22ce";
  } else {
    roleBadge.style.color = "#15803d";
  }
}

// ============================================================
// ROLE-BASED ACCESS PERMISSIONS (Strict Separation)
// ============================================================
function applyRolePermissions() {
  const role = state.currentUser.role;

  // Sidebar link filtering
  const sidebarUsers = document.querySelector('.sidebar-item[data-screen="users"]');
  const sidebarLabs = document.querySelector('.sidebar-item[data-screen="laboratories"]');
  const sidebarAvail = document.querySelector('.sidebar-item[data-screen="availability"]');
  const sidebarBookings = document.querySelector('.sidebar-item[data-screen="bookings"]');
  const sidebarEquipment = document.querySelector('.sidebar-item[data-screen="equipment"]');
  const sidebarSettings = document.querySelector('.sidebar-item[data-screen="settings"]');

  // Reset all
  document.querySelectorAll(".sidebar-item").forEach(item => item.classList.remove("role-hidden"));

  // Customize based on role
  if (role === "Administrator") {
    sidebarBookings.querySelector("span").innerText = "Bookings";
  } else if (role === "Faculty" || role === "Lecturer") {
    if (sidebarUsers) sidebarUsers.classList.add("role-hidden");
    if (sidebarSettings) sidebarSettings.classList.add("role-hidden");
    sidebarBookings.querySelector("span").innerText = "My Bookings";
  } else if (role === "Student" || role === "Graduate Student") {
    if (sidebarUsers) sidebarUsers.classList.add("role-hidden");
    if (sidebarEquipment) sidebarEquipment.classList.add("role-hidden");
    if (sidebarSettings) sidebarSettings.classList.add("role-hidden");
    sidebarBookings.querySelector("span").innerText = "My Bookings";
  } else if (role === "Lab Technician") {
    if (sidebarUsers) sidebarUsers.classList.add("role-hidden");
    if (sidebarSettings) sidebarSettings.classList.add("role-hidden");
  }

  // Quick Action Buttons visibility
  const btnAddLab = document.querySelector('.btn-action-secondary');
  if (btnAddLab) {
    btnAddLab.style.display = (role === "Administrator" || role === "Lab Technician") ? "flex" : "none";
  }
  const btnAddLabHeader = document.querySelector('#screen-laboratories .btn-primary-add');
  if (btnAddLabHeader) {
    btnAddLabHeader.style.display = (role === "Administrator" || role === "Lab Technician") ? "inline-flex" : "none";
  }
  const btnAddEqHeader = document.querySelector('#screen-equipment .btn-primary-add');
  if (btnAddEqHeader) {
    btnAddEqHeader.style.display = (role === "Administrator" || role === "Lab Technician") ? "inline-flex" : "none";
  }
}

// ============================================================
// SCREEN SWITCHING
// ============================================================
function switchScreen(screenId) {
  // Prevent unauthorized screen navigation
  const role = state.currentUser.role;
  if ((role !== "Administrator") && (screenId === "users" || screenId === "settings")) {
    showToast("Access restricted to Administrators.", true);
    return;
  }
  if ((role === "Student" || role === "Graduate Student") && screenId === "equipment") {
    showToast("Access restricted.", true);
    return;
  }

  state.currentScreen = screenId;

  document.querySelectorAll(".sidebar-item").forEach(el => {
    el.classList.toggle("active", el.getAttribute("data-screen") === screenId);
  });

  document.querySelectorAll(".view-section").forEach(sec => {
    sec.classList.remove("active");
  });
  const activeSec = document.getElementById(`screen-${screenId}`);
  if (activeSec) {
    activeSec.classList.add("active");
  }

  const meta = SCREEN_TITLES[screenId] || { title: screenId, subtitle: "" };
  document.getElementById("topbar-title").innerText = meta.title;
  document.getElementById("topbar-subtitle").innerText = meta.subtitle;

  if (screenId === "dashboard") {
    loadDashboardData();
  } else if (screenId === "laboratories") {
    loadLaboratories();
  } else if (screenId === "users") {
    loadUsers();
  } else if (screenId === "availability") {
    loadAvailability();
  } else if (screenId === "bookings") {
    loadBookings();
  } else if (screenId === "equipment") {
    loadEquipment();
  }
}

// ============================================================
// DATA FETCHING & RENDERING
// ============================================================
async function loadAllData() {
  loadDashboardData();
  loadLaboratories();
  loadUsers();
  loadEquipment();
  loadBookings();
  loadAvailability();
}

// 1. Dashboard (Role-Tailored)
async function loadDashboardData() {
  const role = state.currentUser.role;
  const uid = state.currentUser.id;

  try {
    const res = await fetch(`${API_BASE}/stats?role=${encodeURIComponent(role)}&user_id=${uid}`);
    const stats = await res.json();

    const statCards = document.querySelectorAll(".stat-cards-grid .stat-card");
    if (statCards.length >= 4) {
      statCards[0].querySelector(".stat-label").innerText = stats.card1_label;
      statCards[0].querySelector(".stat-value").innerText = stats.card1_value;
      statCards[0].querySelector(".stat-subtext").innerText = stats.card1_sub;

      statCards[1].querySelector(".stat-label").innerText = stats.card2_label;
      statCards[1].querySelector(".stat-value").innerText = stats.card2_value;
      statCards[1].querySelector(".stat-subtext").innerText = stats.card2_sub;

      statCards[2].querySelector(".stat-label").innerText = stats.card3_label;
      statCards[2].querySelector(".stat-value").innerText = stats.card3_value;
      statCards[2].querySelector(".stat-subtext").innerText = stats.card3_sub;

      statCards[3].querySelector(".stat-label").innerText = stats.card4_label;
      statCards[3].querySelector(".stat-value").innerText = stats.card4_value;
      statCards[3].querySelector(".stat-subtext").innerText = stats.card4_sub;
    }
  } catch (e) {
    console.warn("Stats error", e);
  }

  // Render Dashboard Reservations
  try {
    const res = await fetch(`${API_BASE}/bookings?tab=all&role=${encodeURIComponent(role)}&user_id=${uid}`);
    const bookings = await res.json();
    const tbody = document.getElementById("dashboard-reservations-body");
    tbody.innerHTML = "";

    const items = bookings.slice(0, 5);
    if (items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#94a3b8; padding:20px;">No reservations found in SQLite database.</td></tr>`;
    } else {
      items.forEach(b => {
        const tr = document.createElement("tr");
        const statusLower = b.status.toLowerCase();
        tr.innerHTML = `
          <td class="bold-text">${b.laboratory_name}</td>
          <td>${b.requested_by}</td>
          <td>${b.time_slot}</td>
          <td><span class="status-pill ${statusLower}">${b.status}</span></td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (e) {
    console.warn("Bookings error", e);
  }

  // Render Laboratory Availability Quick List
  try {
    const res = await fetch(`${API_BASE}/laboratories`);
    const labs = await res.json();
    const listContainer = document.getElementById("dashboard-avail-list");
    listContainer.innerHTML = "";

    labs.slice(0, 6).forEach(l => {
      let dotColor = "green";
      let statusText = "Available Now";
      if (l.status === "In Use") {
        dotColor = "red";
        statusText = "In Use";
      } else if (l.status === "Maintenance" || l.status === "Under Maintenance") {
        dotColor = "gray";
        statusText = "Maintenance";
      }

      const item = document.createElement("div");
      item.className = "lab-avail-item";
      item.innerHTML = `
        <span class="lab-avail-name">${l.laboratory_name}</span>
        <span class="lab-avail-status">
          <span class="status-dot ${dotColor}"></span>
          ${statusText}
        </span>
      `;
      listContainer.appendChild(item);
    });
  } catch (e) {
    console.warn("Labs error", e);
  }
}

// 2. Laboratories (Full CRUD)
async function loadLaboratories() {
  try {
    const res = await fetch(`${API_BASE}/laboratories`);
    state.laboratories = await res.json();
    renderLaboratories(state.laboratories);
  } catch (e) {
    console.warn(e);
  }
}

function renderLaboratories(labs) {
  const container = document.getElementById("laboratories-grid");
  container.innerHTML = "";
  const role = state.currentUser.role;
  const canEdit = (role === "Administrator" || role === "Lab Technician");

  if (labs.length === 0) {
    container.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: #94a3b8; padding: 40px;">No laboratories found.</p>`;
    return;
  }

  labs.forEach(lab => {
    const statusClass = lab.status.toLowerCase().replace(" ", "-");
    const card = document.createElement("div");
    card.className = `lab-card ${statusClass}`;

    let actionBtns = `
      <span class="lab-card-icon-action" onclick="showToast('${lab.laboratory_name}: Capacity ${lab.capacity}')" title="Details">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
      </span>
    `;

    if (canEdit) {
      actionBtns = `
        <div style="display: flex; align-items: center; gap: 8px;">
          <span class="lab-card-icon-action" onclick="openEditLabModal(${lab.laboratory_id})" title="Edit Facility">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
          </span>
          <span class="lab-card-icon-action" style="color:#ef4444;" onclick="deleteLab(${lab.laboratory_id}, '${lab.laboratory_name}')" title="Delete Facility">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
          </span>
        </div>
      `;
    }

    card.innerHTML = `
      <div style="margin: -20px -20px 15px -20px;">
        <img src="${lab.image_url || 'assets/images/favicon.jpg'}" style="width: 100%; aspect-ratio: 16/9; object-fit: cover; border-radius: 8px 8px 0 0; display: block;">
      </div>
      <div>
        <div class="lab-card-header">
          <div>
            <div class="lab-card-name">${lab.laboratory_name}</div>
            <div class="lab-card-location">${lab.location || 'Science Building, Room 301'}</div>
          </div>
          <span class="status-pill ${statusClass}">
            ${lab.status}
          </span>
        </div>
        <div class="lab-card-meta">
          <div class="lab-meta-item">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle></svg>
            <span>Capacity: ${lab.capacity}</span>
          </div>
          <div class="lab-meta-item">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" y1="21" x2="4" y2="14"></line><line x1="12" y1="21" x2="12" y2="12"></line><line x1="20" y1="21" x2="20" y2="16"></line></svg>
            <span>${lab.equipment_count || 0} Equipment Items</span>
          </div>
        </div>
      </div>
      <div class="lab-card-footer">
        <span>${lab.last_booking}</span>
        ${actionBtns}
      </div>
    `;
    container.appendChild(card);
  });
}

function filterLaboratories() {
  const query = document.getElementById("filter-labs-search").value.toLowerCase();
  const building = document.getElementById("filter-labs-building").value;
  const status = document.getElementById("filter-labs-status").value;

  const filtered = state.laboratories.filter(l => {
    const matchSearch = l.laboratory_name.toLowerCase().includes(query) || (l.location && l.location.toLowerCase().includes(query));
    const matchBuilding = !building || (l.location && l.location.includes(building));
    const matchStatus = !status || l.status === status;
    return matchSearch && matchBuilding && matchStatus;
  });

  renderLaboratories(filtered);
}

function openEditLabModal(labId) {
  const lab = state.laboratories.find(l => l.laboratory_id === labId);
  if (!lab) return;

  document.getElementById("edit-lab-id").value = lab.laboratory_id;
  document.getElementById("edit-lab-name").value = lab.laboratory_name;
  document.getElementById("edit-lab-location").value = lab.location;
  document.getElementById("edit-lab-capacity").value = lab.capacity;
  document.getElementById("edit-lab-status").value = lab.status;
  document.getElementById("edit-lab-img-file").value = "";
  document.getElementById("edit-lab-img-url").value = lab.image_url || "";

  openModal("modal-edit-lab");
}

async function handleUpdateLab(event) {
  event.preventDefault();
  const id = document.getElementById("edit-lab-id").value;
  const name = document.getElementById("edit-lab-name").value.trim();
  const loc = document.getElementById("edit-lab-location").value.trim();
  const cap = document.getElementById("edit-lab-capacity").value;
  const status = document.getElementById("edit-lab-status").value;
  const fileInput = document.getElementById("edit-lab-img-file");
  const urlInput = document.getElementById("edit-lab-img-url").value.trim();
  
  let imgBase64 = "";
  let imgName = "";
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    imgName = file.name;
    try {
      imgBase64 = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
      });
    } catch(e) {
      console.error(e);
    }
  }

  try {
    const res = await fetch(`${API_BASE}/laboratories/update`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ laboratory_id: id, name: name, location: loc, capacity: cap, status: status, image_data: imgBase64, image_name: imgName, image_url: urlInput })
    });
    const data = await res.json();
    if (data.success) {
      closeModal("modal-edit-lab");
      showToast(data.message);
      loadLaboratories();
      loadDashboardData();
    }
  } catch (e) {
    showToast("Failed to update laboratory.", true);
  }
}

async function deleteLab(labId, name) {
  if (!confirm(`Are you sure you want to delete ${name} from SQLite database?`)) return;

  try {
    const res = await fetch(`${API_BASE}/laboratories/delete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ laboratory_id: labId })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message);
      loadLaboratories();
      loadDashboardData();
    }
  } catch (e) {
    showToast("Failed to delete laboratory.", true);
  }
}

// 3. Users (Full CRUD, Admin only)
async function loadUsers() {
  try {
    const res = await fetch(`${API_BASE}/users`);
    state.users = await res.json();
    renderUsers(state.users);
  } catch (e) {
    console.warn(e);
  }
}

function renderUsers(users) {
  const tbody = document.getElementById("users-table-body");
  tbody.innerHTML = "";

  users.forEach(u => {
    let roleClass = "faculty";
    if (u.role_name === "Lab Technician") roleClass = "tech";
    else if (u.role_name === "Administrator") roleClass = "admin";
    else if (u.role_name === "Graduate Student" || u.role_name === "Student") roleClass = "student";

    const initial = u.name ? u.name.split(" ").pop()[0] : "U";

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>
        <div class="user-name-cell">
          <div class="user-initial-badge">${initial}</div>
          <span class="bold-text">${u.name}</span>
        </div>
      </td>
      <td>${u.e_id}</td>
      <td>${u.email}</td>
      <td><span class="role-badge ${roleClass}">${u.role_name}</span></td>
      <td>${u.department || 'Applied Science'}</td>
      <td>
        <span class="status-pill ${u.status === 'Active' ? 'active' : 'inactive'}">
          <span class="status-dot ${u.status === 'Active' ? 'green' : 'gray'}"></span>
          ${u.status}
        </span>
      </td>
      <td>
        <div class="table-action-icons">
          <button type="button" class="action-icon-btn" onclick="openEditUserModal(${u.user_id})" title="Edit User">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
          </button>
          <button type="button" class="action-icon-btn delete" onclick="deleteUser(${u.user_id}, '${u.name}')" title="Delete User">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
          </button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById("users-pagination-info").innerText = `Showing 1-${users.length} of ${users.length} users`;
}

function filterUsers() {
  const query = document.getElementById("filter-users-search").value.toLowerCase();
  const role = document.getElementById("filter-users-role").value;

  const filtered = state.users.filter(u => {
    const matchSearch = u.name.toLowerCase().includes(query) || u.e_id.toLowerCase().includes(query) || u.email.toLowerCase().includes(query);
    const matchRole = !role || u.role_name === role;
    return matchSearch && matchRole;
  });

  renderUsers(filtered);
}

function openEditUserModal(userId) {
  const u = state.users.find(item => item.user_id === userId);
  if (!u) return;

  document.getElementById("edit-user-id").value = u.user_id;
  document.getElementById("edit-user-name").value = u.name;
  document.getElementById("edit-user-email").value = u.email;
  document.getElementById("edit-user-role").value = u.role_id;
  document.getElementById("edit-user-dept").value = u.department || "Chemistry";
  document.getElementById("edit-user-status").value = u.status;

  openModal("modal-edit-user");
}

async function handleUpdateUser(event) {
  event.preventDefault();
  const id = document.getElementById("edit-user-id").value;
  const name = document.getElementById("edit-user-name").value.trim();
  const email = document.getElementById("edit-user-email").value.trim();
  const roleId = document.getElementById("edit-user-role").value;
  const dept = document.getElementById("edit-user-dept").value.trim();
  const status = document.getElementById("edit-user-status").value;

  try {
    const res = await fetch(`${API_BASE}/users/update`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: id, name, email, role_id: roleId, department: dept, status })
    });
    const data = await res.json();
    if (data.success) {
      closeModal("modal-edit-user");
      showToast(data.message);
      loadUsers();
    }
  } catch (e) {
    showToast("Failed to update user.", true);
  }
}

async function deleteUser(userId, name) {
  if (userId === 1) {
    showToast("Cannot delete root administrator!", true);
    return;
  }
  if (!confirm(`Are you sure you want to delete user ${name}?`)) return;

  try {
    const res = await fetch(`${API_BASE}/users/delete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message);
      loadUsers();
    } else {
      showToast(data.message, true);
    }
  } catch (e) {
    showToast("Failed to delete user.", true);
  }
}

// 4. Equipment (Full CRUD)
async function loadEquipment() {
  try {
    const res = await fetch(`${API_BASE}/equipment`);
    state.equipment = await res.json();
    renderEquipment(state.equipment);
  } catch (e) {
    console.warn(e);
  }
}

function renderEquipment(equipmentList) {
  const tbody = document.getElementById("equipment-table-body");
  tbody.innerHTML = "";
  const role = state.currentUser.role;
  const canEdit = (role === "Administrator" || role === "Lab Technician");

  equipmentList.forEach(eq => {
    const tr = document.createElement("tr");
    const statusClass = eq.status.toLowerCase().replace(" ", "-");

    let actionBtns = `
      <button type="button" class="action-icon-btn" onclick="showToast('${eq.equipment_name}: Available ${eq.quantity_available}/${eq.quantity_total}')" title="Details">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
      </button>
    `;

    if (canEdit) {
      actionBtns = `
        <div class="table-action-icons">
          <button type="button" class="action-icon-btn" onclick="openEditEquipmentModal(${eq.equipment_id})" title="Edit Equipment">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
          </button>
          <button type="button" class="action-icon-btn" onclick="scheduleCalibration(${eq.equipment_id}, '${eq.equipment_name}')" title="Schedule Calibration">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
          </button>
          <button type="button" class="action-icon-btn delete" onclick="deleteEquipment(${eq.equipment_id}, '${eq.equipment_name}')" title="Delete Equipment">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
          </button>
        </div>
      `;
    }

    tr.innerHTML = `
      <td class="bold-text">${eq.equipment_name}</td>
      <td>${eq.id_code}</td>
      <td>${eq.laboratory_name}</td>
      <td><span class="category-badge">${eq.category}</span></td>
      <td><span class="status-pill ${statusClass}">${eq.status}</span></td>
      <td>${eq.last_calibration}</td>
      <td>${actionBtns}</td>
    `;
    tbody.appendChild(tr);
  });

  const eqInfo = document.getElementById("equipment-pagination-info");
  if (eqInfo) {
    eqInfo.innerText = `Showing 1-${equipmentList.length} of ${equipmentList.length} equipment units`;
  }
}

function filterEquipment() {
  const query = document.getElementById("filter-equipment-search").value.toLowerCase();
  const lab = document.getElementById("filter-equipment-lab").value;
  const status = document.getElementById("filter-equipment-status").value;

  const filtered = state.equipment.filter(eq => {
    const matchSearch = eq.equipment_name.toLowerCase().includes(query) || (eq.id_code && eq.id_code.toLowerCase().includes(query));
    const matchLab = !lab || eq.laboratory_name === lab;
    const matchStatus = !status || eq.status === status;
    return matchSearch && matchLab && matchStatus;
  });

  renderEquipment(filtered);
}

function openEditEquipmentModal(eqId) {
  const eq = state.equipment.find(item => item.equipment_id === eqId);
  if (!eq) return;

  document.getElementById("edit-eq-id").value = eq.equipment_id;
  document.getElementById("edit-eq-name").value = eq.equipment_name;
  document.getElementById("edit-eq-category").value = eq.category;
  document.getElementById("edit-eq-status").value = eq.status;
  document.getElementById("edit-eq-cal").value = eq.last_calibration;

  openModal("modal-edit-equipment");
}

async function handleUpdateEquipment(event) {
  event.preventDefault();
  const id = document.getElementById("edit-eq-id").value;
  const name = document.getElementById("edit-eq-name").value.trim();
  const cat = document.getElementById("edit-eq-category").value;
  const status = document.getElementById("edit-eq-status").value;
  const cal = document.getElementById("edit-eq-cal").value;

  try {
    const res = await fetch(`${API_BASE}/equipment/update`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ equipment_id: id, name, category: cat, status, last_calibration: cal })
    });
    const data = await res.json();
    if (data.success) {
      closeModal("modal-edit-equipment");
      showToast(data.message);
      loadEquipment();
    }
  } catch (e) {
    showToast("Failed to update equipment.", true);
  }
}

async function scheduleCalibration(eqId, name) {
  const today = new Date().toISOString().split("T")[0];
  try {
    const res = await fetch(`${API_BASE}/equipment/update`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ equipment_id: eqId, name, category: "Measurement", status: "Available", last_calibration: today })
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Calibration logged for ${name} on ${today}!`);
      loadEquipment();
    }
  } catch (e) {
    showToast("Failed to log calibration.", true);
  }
}

async function deleteEquipment(eqId, name) {
  if (!confirm(`Are you sure you want to delete ${name}?`)) return;

  try {
    const res = await fetch(`${API_BASE}/equipment/delete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ equipment_id: eqId })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message);
      loadEquipment();
    }
  } catch (e) {
    showToast("Failed to delete equipment.", true);
  }
}

// 5. Bookings & Approvals (Role separation)
async function loadBookings(tab = state.currentBookingTab) {
  const role = state.currentUser.role;
  const uid = state.currentUser.id;

  try {
    const res = await fetch(`${API_BASE}/bookings?tab=${tab}&role=${encodeURIComponent(role)}&user_id=${uid}`);
    state.bookings = await res.json();
    renderBookings(state.bookings);
  } catch (e) {
    console.warn(e);
  }
}

function renderBookings(bookingsList) {
  const tbody = document.getElementById("bookings-table-body");
  tbody.innerHTML = "";
  const role = state.currentUser.role;
  const uid = state.currentUser.id;
  const isAdmin = (role === "Administrator");

  if (bookingsList.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:#94a3b8; padding:30px;">No reservations match the selected filter.</td></tr>`;
    document.getElementById("bookings-pagination-info").innerText = "Showing 0 bookings";
    return;
  }

  bookingsList.forEach(b => {
    const tr = document.createElement("tr");
    const statusLower = b.status.toLowerCase();

    let actionHtml = `<a class="link-view-details" onclick="openBookingDetailsModal(${b.booking_id})">View Details</a>`;

    if (isAdmin) {
      if (b.status === "Pending") {
        actionHtml = `
          <div class="booking-approval-actions">
            <button type="button" class="btn-approve" onclick="approveBooking(${b.booking_id})">Approve</button>
            <button type="button" class="btn-reject" onclick="rejectBooking(${b.booking_id})">Reject</button>
          </div>
        `;
      }
    } else {
      // Student / Faculty: Can cancel their own pending/confirmed booking
      if (b.user_id === uid && (b.status === "Pending" || b.status === "Confirmed")) {
        actionHtml = `
          <div style="display:flex; align-items:center; gap:8px;">
            <a class="link-view-details" onclick="openBookingDetailsModal(${b.booking_id})">Details</a>
            <button type="button" class="btn-cancel" onclick="cancelBooking(${b.booking_id})">Cancel</button>
          </div>
        `;
      }
    }

    tr.innerHTML = `
      <td class="bold-text">${b.code}</td>
      <td>${b.laboratory_name}</td>
      <td>${b.requested_by}</td>
      <td>${b.booking_date}</td>
      <td>${b.time_slot}</td>
      <td>${b.purpose}</td>
      <td><span class="status-pill ${statusLower}">${b.status}</span></td>
      <td>${actionHtml}</td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById("bookings-pagination-info").innerText = `Showing 1-${bookingsList.length} of ${bookingsList.length} bookings`;
}

function switchBookingTab(btn, tab) {
  state.currentBookingTab = tab;
  document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("active"));
  btn.classList.add("active");
  loadBookings(tab);
}

function filterBookings() {
  const query = document.getElementById("filter-bookings-search").value.toLowerCase();
  const lab = document.getElementById("filter-bookings-lab").value;
  const status = document.getElementById("filter-bookings-status").value;

  const filtered = state.bookings.filter(b => {
    const matchSearch = b.code.toLowerCase().includes(query) || b.requested_by.toLowerCase().includes(query) || b.purpose.toLowerCase().includes(query);
    const matchLab = !lab || b.laboratory_name === lab;
    const matchStatus = !status || b.status === status;
    return matchSearch && matchLab && matchStatus;
  });

  renderBookings(filtered);
}

async function approveBooking(bookingId) {
  try {
    const res = await fetch(`${API_BASE}/bookings/${bookingId}/approve`, { method: "POST" });
    const data = await res.json();
    if (data.success) {
      showToast(data.message);
      loadBookings();
      loadDashboardData();
    }
  } catch (e) {
    showToast("Failed to approve.", true);
  }
}

async function rejectBooking(bookingId) {
  try {
    const res = await fetch(`${API_BASE}/bookings/${bookingId}/reject`, { method: "POST" });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, true);
      loadBookings();
      loadDashboardData();
    }
  } catch (e) {
    showToast("Failed to reject.", true);
  }
}

async function cancelBooking(bookingId) {
  if (!confirm("Are you sure you want to cancel this reservation?")) return;

  try {
    const res = await fetch(`${API_BASE}/bookings/${bookingId}/cancel`, { method: "POST" });
    const data = await res.json();
    if (data.success) {
      showToast(data.message);
      loadBookings();
      loadDashboardData();
    }
  } catch (e) {
    showToast("Failed to cancel booking.", true);
  }
}

// 6. Availability Timetable (Direct from SQLite BOOKINGS)
async function loadAvailability() {
  const selectedLab = document.getElementById("availability-lab-select").value;
  try {
    const res = await fetch(`${API_BASE}/availability?lab=${encodeURIComponent(selectedLab)}`);
    const data = await res.json();
    renderAvailability(data);
  } catch (e) {
    console.warn("Availability load error", e);
  }
}

function renderAvailability(data) {
  document.getElementById("availability-week-label").innerText = data.week_label;
  const tbody = document.getElementById("availability-timetable-body");
  tbody.innerHTML = "";

  data.time_slots.forEach(slot => {
    const tr = document.createElement("tr");
    let rowHtml = `<td>${slot}</td>`;

    data.days.forEach(day => {
      const evt = data.events.find(e => e.day === day.key && e.slot === slot);
      if (evt) {
        rowHtml += `
          <td class="timetable-cell">
            <div class="event-card-block ${evt.type}">
              <div class="event-block-title">${evt.title}</div>
              <div class="event-block-subtitle">${evt.subtitle}</div>
              <div class="event-block-status">${evt.status}</div>
            </div>
          </td>
        `;
      } else {
        rowHtml += `<td class="timetable-cell" onclick="openBookingAtSlot('${day.date}', '${slot}')" title="Click to Reserve Slot"></td>`;
      }
    });

    tr.innerHTML = rowHtml;
    tbody.appendChild(tr);
  });
}

function shiftWeek(offset) {
  state.currentWeekIndex += offset;
  const labels = [
    "Nov 18 – Nov 22, 2024",
    "Nov 25 – Nov 29, 2024",
    "Dec 02 – Dec 06, 2024"
  ];
  const idx = Math.abs(state.currentWeekIndex) % labels.length;
  document.getElementById("availability-week-label").innerText = labels[idx];
  showToast(`Loaded timetable for ${labels[idx]}`);
}

function setAvailView(btn, mode) {
  document.querySelectorAll(".view-toggle-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  showToast(`Switched timetable to ${mode.toUpperCase()} view`);
}

function openBookingAtSlot(dateStr, slot) {
  openModal('modal-booking');
  if (dateStr) document.getElementById("new-booking-date").value = dateStr;
  const [start, end] = slot.split("–").map(s => s.trim());
  if (start) document.getElementById("new-booking-start").value = start.padStart(5, '0');
  if (end) document.getElementById("new-booking-end").value = end.padStart(5, '0');
}


// ============================================================
// MODAL CONTROLLERS & FORM HANDLERS
// ============================================================
function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add("active");
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove("active");
}

function openNewBookingModal() {
  openModal("modal-booking");
}

function openAddLabModal() {
  openModal("modal-add-lab");
}

function openAddUserModal() {
  openModal("modal-add-user");
}

function openAddEquipmentModal() {
  openModal("modal-add-equipment");
}

async function handleCreateBooking(event) {
  event.preventDefault();
  const labId = document.getElementById("new-booking-lab").value;
  const purpose = document.getElementById("new-booking-purpose").value.trim();
  const date = document.getElementById("new-booking-date").value;
  const start = document.getElementById("new-booking-start").value;
  const end = document.getElementById("new-booking-end").value;

  try {
    const res = await fetch(`${API_BASE}/bookings/create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        laboratory_id: parseInt(labId),
        user_id: state.currentUser.id,
        purpose: purpose,
        date: date,
        start_time: start,
        end_time: end
      })
    });
    const data = await res.json();

    if (data.success) {
      closeModal("modal-booking");
      showToast(data.message);
      loadBookings();
      loadAvailability();
      loadDashboardData();
    } else {
      showToast(data.message, true);
    }
  } catch (e) {
    showToast("Error creating reservation.", true);
  }
}

async function handleAddLab(event) {
  event.preventDefault();
  const name = document.getElementById("add-lab-name").value.trim();
  const loc = document.getElementById("add-lab-location").value.trim();
  const cap = document.getElementById("add-lab-capacity").value;
  const status = document.getElementById("add-lab-status").value;
  const fileInput = document.getElementById("add-lab-img-file");
  const urlInput = document.getElementById("add-lab-img-url").value.trim();
  
  let imgBase64 = "";
  let imgName = "";
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    imgName = file.name;
    try {
      imgBase64 = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
      });
    } catch(e) {
      console.error(e);
    }
  }

  try {
    const res = await fetch(`${API_BASE}/laboratories/create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, location: loc, capacity: cap, status, image_data: imgBase64, image_name: imgName, image_url: urlInput })
    });
    const data = await res.json();
    if (data.success) {
      closeModal("modal-add-lab");
      showToast(`Laboratory ${name} added!`);
      loadLaboratories();
      loadDashboardData();
    }
  } catch (e) {
    showToast("Error adding laboratory.", true);
  }
}

async function handleAddUser(event) {
  event.preventDefault();
  const name = document.getElementById("add-user-name").value.trim();
  const eid = document.getElementById("add-user-eid").value.trim();
  const email = document.getElementById("add-user-email").value.trim();
  const roleId = document.getElementById("add-user-role").value;
  const dept = document.getElementById("add-user-dept").value.trim();

  try {
    const res = await fetch(`${API_BASE}/users/create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, e_id: eid, email, role_id: roleId, department: dept })
    });
    const data = await res.json();
    if (data.success) {
      closeModal("modal-add-user");
      showToast(`User ${name} registered!`);
      loadUsers();
    }
  } catch (e) {
    showToast("Error adding user.", true);
  }
}

async function handleAddEquipment(event) {
  event.preventDefault();
  const name = document.getElementById("add-eq-name").value.trim();
  const labId = document.getElementById("add-eq-lab").value;
  const cat = document.getElementById("add-eq-category").value;
  const qty = document.getElementById("add-eq-qty").value;

  try {
    const res = await fetch(`${API_BASE}/equipment/create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, laboratory_id: labId, category: cat, quantity: qty })
    });
    const data = await res.json();
    if (data.success) {
      closeModal("modal-add-equipment");
      showToast(`Equipment ${name} registered!`);
      loadEquipment();
    }
  } catch (e) {
    showToast("Error adding equipment.", true);
  }
}

function openBookingDetailsModal(bookingId) {
  const b = state.bookings.find(item => item.booking_id === bookingId);
  if (!b) return;

  document.getElementById("details-modal-title").innerText = `Reservation ${b.code}`;
  document.getElementById("details-modal-content").innerHTML = `
    <p><strong>Laboratory:</strong> ${b.laboratory_name}</p>
    <p><strong>Reserved By:</strong> ${b.requested_by} (${b.e_id || 'Verified'})</p>
    <p><strong>Date:</strong> ${b.booking_date}</p>
    <p><strong>Scheduled Slot:</strong> ${b.time_slot}</p>
    <p><strong>Purpose:</strong> ${b.purpose}</p>
    <p><strong>Approval Status:</strong> <span class="status-pill ${b.status.toLowerCase()}">${b.status}</span></p>
    <p><strong>Collision Guard:</strong> Verified (Double-booking check active)</p>
  `;
  openModal("modal-details");
}

// ============================================================
// TOAST NOTIFICATIONS
// ============================================================
function showToast(message, isError = false) {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = "toast";
  if (isError) {
    toast.style.backgroundColor = "#dc2626";
  }

  toast.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.3s";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
