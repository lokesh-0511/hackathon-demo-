/**
 * CultPulse 2026 - Frontend Application Logic
 */

let allEvents = [];
let activeCategory = 'All';
let currentSearch = '';
let qrcodeInstance = null;
let searchDebounceTimer = null;

// On Page Load
document.addEventListener('DOMContentLoaded', () => {
    fetchEvents();
});

// View Navigation Switcher
function switchView(viewId) {
    // Hide all sections
    ['events-view', 'aid-view', 'organizer-view'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add('hidden');
    });

    // Show target section
    const target = document.getElementById(viewId);
    if (target) target.classList.remove('hidden');

    // Update Desktop Nav styles
    const navMap = {
        'events-view': 'nav-events',
        'aid-view': 'nav-aid',
        'organizer-view': 'nav-organizer'
    };

    const mobileNavMap = {
        'events-view': 'm-nav-events',
        'aid-view': 'm-nav-aid',
        'organizer-view': 'm-nav-organizer'
    };

    ['nav-events', 'nav-aid', 'nav-organizer'].forEach(btnId => {
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.className = "nav-tab px-5 py-2 rounded-full transition-all duration-200 text-slate-400 hover:text-white";
        }
    });

    ['m-nav-events', 'm-nav-aid', 'm-nav-organizer'].forEach(btnId => {
        const btn = document.getElementById(btnId);
        if (btn) {
            btn.className = "mobile-nav flex flex-col items-center gap-1 text-slate-400 py-1";
        }
    });

    if (navMap[viewId] && document.getElementById(navMap[viewId])) {
        document.getElementById(navMap[viewId]).className = "nav-tab active px-5 py-2 rounded-full transition-all duration-200 text-white bg-gradient-to-r from-fuchsia-600 to-pink-600 shadow-md";
    }

    if (mobileNavMap[viewId] && document.getElementById(mobileNavMap[viewId])) {
        document.getElementById(mobileNavMap[viewId]).className = "mobile-nav flex flex-col items-center gap-1 text-fuchsia-400 py-1 font-bold";
    }

    // If Organizer Hub selected, fetch dashboard metrics
    if (viewId === 'organizer-view') {
        fetchOrganizerData();
    }
}

// Fetch Events from API
async function fetchEvents() {
    try {
        const res = await fetch('/api/events');
        const data = await res.json();
        if (data.success) {
            allEvents = data.events;
            populateEventSelectDropdown();
            renderEvents();
        }
    } catch (err) {
        console.error("Failed to load events", err);
        showToast("Error connecting to server. Please check backend.", "error");
    }
}

// Filter Category
function filterCategory(cat) {
    activeCategory = cat;
    document.querySelectorAll('.cat-pill').forEach(pill => {
        if (pill.textContent.includes(cat) || (cat === 'All' && pill.textContent.includes('All Events'))) {
            pill.className = "cat-pill active px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition bg-fuchsia-600 text-white shadow-md";
        } else {
            pill.className = "cat-pill px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition bg-slate-900 text-slate-400 hover:text-white border border-slate-800";
        }
    });
    renderEvents();
}

// Search Filter
function handleSearchEvents() {
    const input = document.getElementById('event-search-input');
    currentSearch = input.value.trim().toLowerCase();
    renderEvents();
}

// Render Event Cards
function renderEvents() {
    const grid = document.getElementById('events-grid');
    if (!grid) return;

    let filtered = allEvents.filter(ev => {
        const matchesCat = (activeCategory === 'All') || (ev.category.toLowerCase() === activeCategory.toLowerCase());
        const matchesSearch = !currentSearch ||
            ev.title.toLowerCase().includes(currentSearch) ||
            ev.description.toLowerCase().includes(currentSearch) ||
            ev.venue.toLowerCase().includes(currentSearch) ||
            ev.category.toLowerCase().includes(currentSearch);
        return matchesCat && matchesSearch;
    });

    if (filtered.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full py-16 text-center text-slate-500 bg-slate-900/40 rounded-3xl border border-slate-800">
                <i class="fa-solid fa-magnifying-glass text-4xl mb-3 text-slate-600"></i>
                <p class="text-base font-semibold text-slate-300">No events matched your search.</p>
                <p class="text-xs text-slate-500 mt-1">Try another keyword or category.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = filtered.map(ev => {
        const isFull = ev.slots_left <= 0;
        const progressPct = Math.min(100, Math.round((ev.registered_count / ev.max_slots) * 100));

        // Category Badge Color
        let catColor = "bg-fuchsia-500/15 text-fuchsia-400 border-fuchsia-500/30";
        if (ev.category === 'Music') catColor = "bg-indigo-500/15 text-indigo-400 border-indigo-500/30";
        if (ev.category === 'Theatre') catColor = "bg-amber-500/15 text-amber-400 border-amber-500/30";
        if (ev.category === 'Fashion') catColor = "bg-pink-500/15 text-pink-400 border-pink-500/30";
        if (ev.category === 'Fine Arts') catColor = "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
        if (ev.category === 'Gaming') catColor = "bg-cyan-500/15 text-cyan-400 border-cyan-500/30";

        return `
            <div class="event-card bg-[#131b2e] rounded-3xl border border-slate-800/90 overflow-hidden flex flex-col group relative">
                <!-- Cover Image -->
                <div class="relative h-44 w-full overflow-hidden bg-slate-900">
                    <img src="${ev.image_url}" alt="${ev.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500">
                    <div class="absolute inset-0 bg-gradient-to-t from-[#131b2e] via-transparent to-black/40"></div>
                    
                    <!-- Top Badges -->
                    <div class="absolute top-3 left-3 flex items-center gap-2">
                        <span class="px-3 py-1 rounded-full text-[11px] font-bold border backdrop-blur-md ${catColor}">
                            ${ev.category}
                        </span>
                        <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-slate-900/80 backdrop-blur-md text-slate-300 border border-slate-700">
                            <i class="fa-solid fa-users text-xs mr-1"></i>${ev.team_type}
                        </span>
                    </div>

                    <!-- Prize Tag -->
                    <div class="absolute bottom-3 right-3 bg-amber-400 text-slate-950 font-black text-xs px-3 py-1 rounded-xl shadow-lg flex items-center gap-1">
                        <i class="fa-solid fa-trophy text-[11px]"></i> ${ev.prize_pool}
                    </div>
                </div>

                <!-- Card Body -->
                <div class="p-5 flex-1 flex flex-col justify-between space-y-4">
                    <div class="space-y-2">
                        <h3 class="text-lg font-bold text-white group-hover:text-fuchsia-300 transition line-clamp-1">${ev.title}</h3>
                        <p class="text-xs text-slate-400 line-clamp-2 leading-relaxed">${ev.description}</p>
                    </div>

                    <!-- Schedule & Venue Details -->
                    <div class="space-y-1.5 text-xs text-slate-300 bg-slate-900/60 p-3 rounded-2xl border border-slate-800/80">
                        <div class="flex items-center gap-2">
                            <i class="fa-regular fa-clock text-fuchsia-400 w-4"></i>
                            <span class="truncate">${ev.date_time}</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <i class="fa-solid fa-location-dot text-pink-400 w-4"></i>
                            <span class="truncate">${ev.venue}</span>
                        </div>
                    </div>

                    <!-- Rules Preview Accordion -->
                    <details class="text-xs text-slate-400 group/details cursor-pointer">
                        <summary class="font-semibold text-slate-300 hover:text-white flex items-center justify-between list-none py-1">
                            <span><i class="fa-solid fa-circle-info text-indigo-400 mr-1.5"></i>Rules & Guidelines</span>
                            <i class="fa-solid fa-chevron-down text-[10px] transition group-open/details:rotate-180"></i>
                        </summary>
                        <div class="mt-2 text-[11px] text-slate-400 p-2.5 bg-slate-950/80 rounded-xl border border-slate-800 leading-relaxed">
                            ${ev.rules}
                            <div class="mt-2 pt-2 border-t border-slate-800 text-slate-400 flex items-center justify-between">
                                <span>Lead: ${ev.coordinator_name}</span>
                                <span class="font-mono text-fuchsia-400">${ev.coordinator_contact}</span>
                            </div>
                        </div>
                    </details>

                    <!-- Slots Progress & Action Button -->
                    <div class="space-y-2.5 pt-2 border-t border-slate-800">
                        <div class="flex items-center justify-between text-[11px]">
                            <span class="text-slate-400">Available Slots:</span>
                            <span class="font-bold ${isFull ? 'text-red-400' : (ev.slots_left <= 5 ? 'text-amber-400' : 'text-emerald-400')}">
                                ${isFull ? 'Housefull' : `${ev.slots_left} of ${ev.max_slots} left`}
                            </span>
                        </div>
                        <!-- Mini Progress Bar -->
                        <div class="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                            <div class="h-full bg-gradient-to-r from-fuchsia-500 to-pink-500 transition-all duration-300" style="width: ${progressPct}%"></div>
                        </div>

                        <button 
                            onclick="openRegisterModal(${ev.id})" 
                            ${isFull ? 'disabled' : ''} 
                            class="w-full py-2.5 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition duration-200 ${
                                isFull 
                                ? 'bg-slate-800 text-slate-500 cursor-not-allowed' 
                                : 'bg-gradient-to-r from-fuchsia-600 to-pink-600 hover:brightness-110 text-white shadow-md shadow-fuchsia-600/20 active:scale-[0.98]'
                            }">
                            <i class="fa-solid fa-ticket"></i>
                            <span>${isFull ? 'Registration Full' : 'Register for Event'}</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Populate the select dropdown inside the registration modal
function populateEventSelectDropdown() {
    const select = document.getElementById('reg-event-select');
    const adminSelect = document.getElementById('admin-event-filter');
    if (!select) return;

    select.innerHTML = allEvents.map(ev => `
        <option value="${ev.id}">${ev.title} (${ev.category} - ${ev.team_type})</option>
    `).join('');

    if (adminSelect) {
        adminSelect.innerHTML = `<option value="all">All Events</option>` + allEvents.map(ev => `
            <option value="${ev.id}">${ev.title}</option>
        `).join('');
    }
}

// When selected event changes in registration modal
function handleEventSelectChange() {
    const select = document.getElementById('reg-event-select');
    const eventId = parseInt(select.value);
    const ev = allEvents.find(e => e.id === eventId);
    if (!ev) return;

    // Show/hide team details section if Solo vs Group
    const teamSection = document.getElementById('team-section');
    if (ev.team_type.toLowerCase().includes('solo')) {
        teamSection.classList.add('hidden');
    } else {
        teamSection.classList.remove('hidden');
    }

    // Detail banner
    const banner = document.getElementById('event-detail-banner');
    banner.innerHTML = `
        <div><i class="fa-regular fa-clock text-pink-400 mr-1"></i> ${ev.date_time}</div>
        <div><i class="fa-solid fa-location-dot text-fuchsia-400 mr-1"></i> ${ev.venue}</div>
        <div><i class="fa-solid fa-trophy text-amber-400 mr-1"></i> Prize: ${ev.prize_pool}</div>
        <div><i class="fa-solid fa-users text-cyan-400 mr-1"></i> Type: ${ev.team_type}</div>
    `;
}

// Open Registration Modal
function openRegisterModal(preselectedEventId = null) {
    const modal = document.getElementById('register-modal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');

    const select = document.getElementById('reg-event-select');
    if (preselectedEventId && select) {
        select.value = preselectedEventId;
    }
    handleEventSelectChange();
}

function closeRegisterModal() {
    const modal = document.getElementById('register-modal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

// Submit Registration
async function submitRegistration(e) {
    e.preventDefault();
    const submitBtn = document.getElementById('reg-submit-btn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Securing Pass...`;

    const payload = {
        event_id: parseInt(document.getElementById('reg-event-select').value),
        name: document.getElementById('reg-name').value.trim(),
        student_name: document.getElementById('reg-name').value.trim(),
        roll_no: document.getElementById('reg-roll').value.trim(),
        branch: document.getElementById('reg-branch').value.trim(),
        department: document.getElementById('reg-branch').value.trim(),
        mobile: document.getElementById('reg-mobile').value.trim(),
        phone: document.getElementById('reg-mobile').value.trim(),
        email: document.getElementById('reg-email').value.trim(),
        college_name: document.getElementById('reg-college').value.trim(),
        year_of_study: document.getElementById('reg-year').value,
        team_name: document.getElementById('reg-team-name') ? document.getElementById('reg-team-name').value.trim() : '',
        team_members: document.getElementById('reg-team-members') ? document.getElementById('reg-team-members').value.trim() : '',
        needs_hostel_aid: document.getElementById('reg-hostel').checked,
        special_requirements: document.getElementById('reg-special').value.trim()
    };

    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await res.json();
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-sparkles"></i> Confirm & Generate Digital E-Pass`;

        if (!result.success) {
            showToast(result.message, "error");
            return;
        }

        // Success!
        closeRegisterModal();
        document.getElementById('fest-registration-form').reset();

        // Trigger celebratory confetti
        triggerConfetti();

        // Display Generated Digital Pass Modal
        displayDigitalPass(result.ticket);

        // Refresh event slots data
        fetchEvents();

    } catch (err) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-sparkles"></i> Confirm & Generate Digital E-Pass`;
        showToast("Network error submitting registration", "error");
    }
}

// Display Digital Fest Pass Modal
function displayDigitalPass(ticket) {
    document.getElementById('pass-ticket-id').innerText = ticket.ticket_id;
    document.getElementById('pass-event-title').innerText = ticket.event_title;
    document.getElementById('pass-student-name').innerText = ticket.name || ticket.student_name;
    document.getElementById('pass-roll-no').innerText = `USN: ${ticket.roll_no}`;
    
    if (document.getElementById('pass-branch')) {
        document.getElementById('pass-branch').innerText = ticket.branch || ticket.department;
    }
    if (document.getElementById('pass-mobile')) {
        document.getElementById('pass-mobile').innerText = ticket.mobile || ticket.phone;
    }
    if (document.getElementById('pass-college')) {
        document.getElementById('pass-college').innerText = ticket.college_name || 'Main Campus';
    }
    if (document.getElementById('pass-dept')) {
        document.getElementById('pass-dept').innerText = `${ticket.branch || ticket.department} (${ticket.year_of_study})`;
    }

    document.getElementById('pass-date-time').innerText = ticket.date_time;
    document.getElementById('pass-venue').innerText = ticket.venue;
    document.getElementById('pass-timestamp').innerText = `Issued: ${new Date().toLocaleTimeString()} • ${ticket.mobile || ticket.phone}`;

    // Team row
    const teamRow = document.getElementById('pass-team-row');
    if (ticket.team_name) {
        teamRow.classList.remove('hidden');
        document.getElementById('pass-team-name').innerText = `${ticket.team_name} ${ticket.team_members ? `(${ticket.team_members})` : ''}`;
    } else {
        teamRow.classList.add('hidden');
    }

    // Aid Tag
    const aidTag = document.getElementById('pass-aid-tag');
    if (ticket.needs_hostel_aid) {
        aidTag.innerHTML = `
            <span class="px-2.5 py-1 rounded-md bg-pink-500/20 text-pink-300 font-bold border border-pink-500/40">
                <i class="fa-solid fa-bed mr-1"></i> Hostel Aid Allocated
            </span>
            ${ticket.special_requirements ? `<span class="text-slate-400 italic">"${ticket.special_requirements}"</span>` : ''}
        `;
    } else {
        aidTag.innerHTML = `
            <span class="px-2.5 py-0.5 rounded-md bg-slate-800 text-slate-400 border border-slate-700">
                Day Participant
            </span>
        `;
    }

    // Render QR Code
    const qrContainer = document.getElementById('qrcode');
    qrContainer.innerHTML = '';
    const qrPayload = JSON.stringify({
        ticket_id: ticket.ticket_id,
        name: ticket.name || ticket.student_name,
        roll: ticket.roll_no,
        branch: ticket.branch || ticket.department,
        mobile: ticket.mobile || ticket.phone,
        event: ticket.event_title
    });

    qrcodeInstance = new QRCode(qrContainer, {
        text: qrPayload,
        width: 80,
        height: 80,
        colorDark: "#000000",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.M
    });

    const passModal = document.getElementById('pass-modal');
    passModal.classList.remove('hidden');
    passModal.classList.add('flex');
}

function closePassModal() {
    const passModal = document.getElementById('pass-modal');
    passModal.classList.add('hidden');
    passModal.classList.remove('flex');
}

// Confetti Celebration
function triggerConfetti() {
    if (typeof confetti === 'function') {
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 }
        });
    }
}

// Submit Student Aid / Helpdesk Query
async function submitHelpdeskQuery(e) {
    e.preventDefault();
    const btn = document.getElementById('hd-submit-btn');
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> Submitting Request...`;

    const payload = {
        student_name: document.getElementById('hd-name').value.trim(),
        contact_info: document.getElementById('hd-contact').value.trim(),
        college_name: document.getElementById('hd-college').value.trim(),
        category: document.getElementById('hd-category').value,
        query_text: document.getElementById('hd-query').value.trim()
    };

    try {
        const res = await fetch('/api/helpdesk', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-paper-plane"></i> Submit Aid Request`;

        if (data.success) {
            showToast("Your college aid request has been received! Our support coordinators will reach out.", "success");
            document.getElementById('helpdesk-form').reset();
        } else {
            showToast(data.message, "error");
        }
    } catch (err) {
        btn.disabled = false;
        btn.innerHTML = `<i class="fa-solid fa-paper-plane"></i> Submit Aid Request`;
        showToast("Error submitting helpdesk query", "error");
    }
}

// ================= ORGANIZER HUB LOGIC =================
async function fetchOrganizerData() {
    const eventFilter = document.getElementById('admin-event-filter') ? document.getElementById('admin-event-filter').value : 'all';
    const searchVal = document.getElementById('admin-search-input') ? document.getElementById('admin-search-input').value.trim() : '';

    try {
        // Fetch stats
        const statsRes = await fetch('/api/stats');
        const statsData = await statsRes.json();
        if (statsData.success) {
            document.getElementById('stat-total-reg').innerText = statsData.total_registrations;
            document.getElementById('stat-total-colleges').innerText = statsData.total_colleges;
            document.getElementById('stat-hostel-requests').innerText = statsData.hostel_requests;
            document.getElementById('stat-checked-in').innerText = statsData.checked_in_count;
        }

        // Fetch Registrations Table
        const regUrl = `/api/registrations?event_id=${encodeURIComponent(eventFilter)}&search=${encodeURIComponent(searchVal)}`;
        const regRes = await fetch(regUrl);
        const regData = await regRes.json();
        if (regData.success) {
            renderRegistrationsTable(regData.registrations);
        }

        // Fetch Helpdesk Requests
        const hdRes = await fetch('/api/helpdesk');
        const hdData = await hdRes.json();
        if (hdData.success) {
            renderHelpdeskTable(hdData.queries);
        }
    } catch (err) {
        console.error("Error loading organizer data", err);
    }
}

function debounceOrganizerSearch() {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
        fetchOrganizerData();
    }, 300);
}

function renderRegistrationsTable(registrations) {
    const tbody = document.getElementById('registrations-table-body');
    if (!tbody) return;

    if (!registrations || registrations.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="p-8 text-center text-slate-500">
                    No registrations found matching criteria.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = registrations.map(r => {
        const isCheckedIn = r.checked_in === 1;
        const branchName = r.branch || r.department || 'N/A';
        const mobileNum = r.mobile || r.phone || 'N/A';
        const studentName = r.name || r.student_name;

        return `
            <tr class="hover:bg-slate-900/60 transition">
                <td class="p-4 font-mono font-bold text-fuchsia-400 whitespace-nowrap">
                    ${r.ticket_id}
                </td>
                <td class="p-4">
                    <div class="font-bold text-white">${studentName}</div>
                    <div class="text-[11px] text-fuchsia-300 font-mono font-semibold">${r.roll_no}</div>
                </td>
                <td class="p-4">
                    <span class="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 whitespace-nowrap">
                        ${branchName}
                    </span>
                </td>
                <td class="p-4 text-slate-300 font-mono text-xs whitespace-nowrap">
                    <i class="fa-solid fa-phone text-[10px] text-slate-500 mr-1"></i>${mobileNum}
                </td>
                <td class="p-4 text-slate-200">
                    <span class="font-semibold">${r.event_title}</span>
                </td>
                <td class="p-4">
                    ${r.team_name ? `<span class="text-pink-400 font-semibold">${r.team_name}</span>` : '<span class="text-slate-500">Solo Entry</span>'}
                </td>
                <td class="p-4">
                    ${r.needs_hostel_aid === 1 ? '<span class="text-amber-400 font-bold"><i class="fa-solid fa-bed mr-1"></i>Yes</span>' : '<span class="text-slate-500">No</span>'}
                </td>
                <td class="p-4">
                    <span class="px-2.5 py-1 rounded-full text-[10px] font-bold ${
                        isCheckedIn 
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' 
                        : 'bg-slate-800 text-slate-400 border border-slate-700'
                    }">
                        ${isCheckedIn ? 'Checked In' : 'Not Checked In'}
                    </span>
                </td>
                <td class="p-4 text-center whitespace-nowrap">
                    <button onclick="toggleCheckIn('${r.ticket_id}')" class="px-3 py-1.5 rounded-lg text-[11px] font-semibold transition ${
                        isCheckedIn 
                        ? 'bg-slate-800 hover:bg-slate-700 text-slate-300' 
                        : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm'
                    }">
                        ${isCheckedIn ? 'Undo Check-in' : '<i class="fa-solid fa-check mr-1"></i> Check In'}
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderHelpdeskTable(queries) {
    const tbody = document.getElementById('helpdesk-table-body');
    if (!tbody) return;

    if (!queries || queries.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="p-6 text-center text-slate-500">
                    No active student aid queries.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = queries.map(q => `
        <tr class="hover:bg-slate-900/60 transition">
            <td class="p-4 font-bold text-white">${q.student_name}</td>
            <td class="p-4 text-slate-300 font-mono text-[11px]">${q.contact_info}</td>
            <td class="p-4 text-slate-300">${q.college_name || 'N/A'}</td>
            <td class="p-4">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-pink-500/20 text-pink-300 border border-pink-500/30">
                    ${q.category}
                </span>
            </td>
            <td class="p-4 text-slate-300 max-w-xs">${q.query_text}</td>
            <td class="p-4 text-slate-500 text-[11px] whitespace-nowrap">${q.created_at}</td>
        </tr>
    `).join('');
}

// Quick Gate Check-in Simulator
async function handleQuickVerify() {
    const input = document.getElementById('quick-ticket-input');
    const ticketId = input.value.trim().toUpperCase();
    if (!ticketId) {
        showToast("Please enter a Ticket ID to verify", "info");
        return;
    }
    await toggleCheckIn(ticketId);
    input.value = '';
}

// Toggle Check-in for a ticket
async function toggleCheckIn(ticketId) {
    try {
        const res = await fetch(`/api/verify/${encodeURIComponent(ticketId)}`, {
            method: 'POST'
        });
        const data = await res.json();
        if (data.success) {
            showToast(`${data.message} (${data.student_name})`, "success");
            fetchOrganizerData();
        } else {
            showToast(data.message, "error");
        }
    } catch (err) {
        showToast("Error updating check-in status", "error");
    }
}

// Toast Alert Utility
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;

    let icon = '<i class="fa-solid fa-circle-info text-cyan-400"></i>';
    let borderStyle = 'border-slate-700 bg-slate-900 text-white';

    if (type === 'success') {
        icon = '<i class="fa-solid fa-circle-check text-emerald-400 text-lg"></i>';
        borderStyle = 'border-emerald-500/40 bg-[#0d1f19] text-emerald-100';
    } else if (type === 'error') {
        icon = '<i class="fa-solid fa-triangle-exclamation text-rose-400 text-lg"></i>';
        borderStyle = 'border-rose-500/40 bg-[#251015] text-rose-100';
    }

    toast.className = `fixed bottom-6 right-6 z-50 transform transition-all duration-300 flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-2xl text-sm font-semibold border ${borderStyle}`;
    toast.innerHTML = `${icon} <span>${message}</span>`;

    // Animate in
    toast.classList.remove('translate-y-24', 'opacity-0');

    setTimeout(() => {
        toast.classList.add('translate-y-24', 'opacity-0');
    }, 4000);
}

