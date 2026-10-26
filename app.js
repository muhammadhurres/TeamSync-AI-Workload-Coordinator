/**
 * TeamSync AI — Frontend Application Logic
 * Role-based auth (Sign In / Sign Up), Lead Dashboard, Candidate Dashboard,
 * personalized task cards, count-up animation, XSS-safe rendering.
 */

document.addEventListener("DOMContentLoaded", () => {

  // ─── Auth & Session State ───────────────────────────────────────────────────
  let currentUser = null;           // Populated after successful login/register
  let currentCredentials = null;    // Kept in memory only for authenticated API requests
  let latestCoordinationResult = null;
  let activeFilter = "all";
  let activeRole = "lead";          // Role selected in login modal tabs
  let authMode = "login";           // "login" | "signup"

  // ─── DOM: Auth Modal ────────────────────────────────────────────────────────
  const loginModal          = document.getElementById("login-modal");
  const tabLead             = document.getElementById("tab-lead");
  const tabCandidate        = document.getElementById("tab-candidate");
  const modeBtnLogin        = document.getElementById("mode-btn-login");
  const modeBtnSignup       = document.getElementById("mode-btn-signup");
  const presetBtnsLead      = document.getElementById("preset-buttons-lead");
  const presetBtnsCand      = document.getElementById("preset-buttons-candidate");
  const authForm            = document.getElementById("auth-form");
  const authUsername        = document.getElementById("auth-username");
  const authPassword        = document.getElementById("auth-password");
  const authRoleInput       = document.getElementById("auth-role");
  const authErrorMsg        = document.getElementById("auth-error-msg");
  const signupExtraFields   = document.getElementById("signup-extra-fields");
  const authDisplayName     = document.getElementById("auth-display-name");
  const authSkills          = document.getElementById("auth-skills");
  const authHours           = document.getElementById("auth-hours");
  const btnAuthText         = document.getElementById("btn-auth-text");
  const groupSkills         = document.getElementById("group-skills");
  const groupHours          = document.getElementById("group-hours");
  const allPresetBtns       = document.querySelectorAll(".btn-preset");

  // ─── DOM: Header ────────────────────────────────────────────────────────────
  const headerUserAvatar    = document.getElementById("header-user-avatar");
  const headerUserName      = document.getElementById("header-user-name");
  const headerUserRole      = document.getElementById("header-user-role");
  const headerBadgeRole     = document.getElementById("header-badge-role");
  const headerLeadDesc      = document.getElementById("header-lead-desc");
  const btnSwitchUser       = document.getElementById("btn-switch-user");

  // ─── DOM: Lead Dashboard Inputs ─────────────────────────────────────────────
  const membersTbody        = document.getElementById("members-tbody");
  const tasksTbody          = document.getElementById("tasks-tbody");
  const btnAddMember        = document.getElementById("btn-add-member");
  const btnAddTask          = document.getElementById("btn-add-task");
  const btnLoadSample       = document.getElementById("btn-load-sample");
  const btnGenerate         = document.getElementById("btn-generate");
  const btnRetry            = document.getElementById("btn-retry");

  // ─── DOM: Dashboard Views ───────────────────────────────────────────────────
  const leadView            = document.getElementById("lead-dashboard-view");
  const candidateView       = document.getElementById("candidate-dashboard-view");

  // ─── DOM: Candidate Profile ──────────────────────────────────────────────────
  const candAvatar          = document.getElementById("cand-avatar");
  const candDisplayName     = document.getElementById("cand-display-name");
  const candBio             = document.getElementById("cand-bio");
  const candSkills          = document.getElementById("cand-skills");
  const candHours           = document.getElementById("cand-hours");
  const candStatus          = document.getElementById("cand-status");
  const candAssignedHours   = document.getElementById("cand-assigned-hours");
  const candTeamSummary     = document.getElementById("cand-team-summary");
  const candidateGrid       = document.getElementById("candidate-assignments-grid");

  // ─── DOM: Results Section (Lead) ────────────────────────────────────────────
  const resultsSection      = document.getElementById("results-section");
  const scoreValue          = document.getElementById("score-value");
  const executiveSummaryText= document.getElementById("executive-summary-text");
  const metaMemberCount     = document.getElementById("meta-member-count");
  const metaTaskCount       = document.getElementById("meta-task-count");
  const metaEngineMode      = document.getElementById("meta-engine-mode");
  const assignmentsGrid     = document.getElementById("assignments-grid");

  // ─── DOM: Utilities ─────────────────────────────────────────────────────────
  const toast               = document.getElementById("toast");
  const toastMessage        = document.getElementById("toast-message");
  const errorBanner         = document.getElementById("error-banner");
  const alertTitle          = document.getElementById("alert-title");
  const alertMessage        = document.getElementById("alert-message");
  const engineStatusText    = document.getElementById("engine-status-text");

  // ─── Sample Data ─────────────────────────────────────────────────────────────
  const BASE_SAMPLE_MEMBERS = [
    { name: "Alex Chen",    skills: "Frontend, React, UI/UX, CSS",      hours: 12 },
    { name: "Samira Patel", skills: "Backend, Python, FastAPI, API",     hours: 10 },
    { name: "Taylor Reed",  skills: "Data Science, PyTorch, Pitch Deck", hours: 8  },
  ];
  const BASE_SAMPLE_TASKS = [
    { title: "Design responsive dashboard layout",       required_skill: "UI/UX",      hours: 3 },
    { title: "Implement kinetic CSS animations & cards", required_skill: "Frontend",   hours: 4 },
    { title: "Build FastAPI coordination endpoint",      required_skill: "Backend",    hours: 4 },
    { title: "Integrate OpenRouter model pipeline",      required_skill: "Python",     hours: 3 },
    { title: "Prepare demo pitch presentation",          required_skill: "Pitch Deck", hours: 2 },
  ];

  // ─── Utility Helpers ─────────────────────────────────────────────────────────
  function showToast(msg) {
    toastMessage.textContent = msg;
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 3500);
  }
  function showError(title, msg) {
    alertTitle.textContent   = title;
    alertMessage.textContent = msg;
    errorBanner.classList.remove("hidden");
    errorBanner.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
  function hideError() { errorBanner.classList.add("hidden"); }
  function showAuthError(msg) {
    authErrorMsg.textContent = msg;
    authErrorMsg.classList.remove("hidden");
  }
  function hideAuthError() { authErrorMsg.classList.add("hidden"); }

  function getAuthenticatedHeaders(headers = {}) {
    if (!currentCredentials) throw new Error("Please sign in again to continue.");
    const bytes = new TextEncoder().encode(
      `${currentCredentials.username}:${currentCredentials.password}`
    );
    const encoded = btoa(Array.from(bytes, byte => String.fromCharCode(byte)).join(""));
    return { ...headers, Authorization: `Basic ${encoded}` };
  }

  // ─── Auth Modal: Role Tab Switching ──────────────────────────────────────────
  function setActiveRole(role) {
    activeRole = role;
    authRoleInput.value = role;

    // Toggle tab styles
    tabLead.classList.toggle("active", role === "lead");
    tabCandidate.classList.toggle("active", role === "candidate");

    // Toggle preset button groups
    presetBtnsLead.classList.toggle("hidden", role !== "lead");
    presetBtnsCand.classList.toggle("hidden", role !== "candidate");

    // Hide skills/hours fields for lead signup (they don't need them)
    if (role === "lead") {
      groupSkills.classList.add("hidden");
      groupHours.classList.add("hidden");
    } else {
      groupSkills.classList.remove("hidden");
      groupHours.classList.remove("hidden");
    }

    updateAuthButtonLabel();
    hideAuthError();
  }

  // ─── Auth Modal: Sign In / Sign Up Mode Toggle ────────────────────────────────
  function setAuthMode(mode) {
    authMode = mode;
    modeBtnLogin.classList.toggle("active", mode === "login");
    modeBtnSignup.classList.toggle("active", mode === "signup");

    signupExtraFields.classList.toggle("hidden", mode === "login");

    // Quick demo buttons only make sense for sign-in
    document.getElementById("quick-demo-container").classList.toggle("hidden", mode === "signup");

    updateAuthButtonLabel();
    hideAuthError();
  }

  function updateAuthButtonLabel() {
    const roleLabel = activeRole === "lead" ? "Team Lead" : "Candidate";
    btnAuthText.textContent = authMode === "login"
      ? `Sign In as ${roleLabel}`
      : `Create ${roleLabel} Account`;
  }

  tabLead.addEventListener("click",      () => setActiveRole("lead"));
  tabCandidate.addEventListener("click", () => setActiveRole("candidate"));
  modeBtnLogin.addEventListener("click",  () => setAuthMode("login"));
  modeBtnSignup.addEventListener("click", () => setAuthMode("signup"));

  // ─── Auth: Preset 1-Click Buttons ────────────────────────────────────────────
  allPresetBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const u    = btn.getAttribute("data-user");
      const p    = btn.getAttribute("data-pass");
      const role = btn.getAttribute("data-role");
      performAuth("login", u, p, role);
    });
  });

  // ─── Auth: Form Submit ────────────────────────────────────────────────────────
  authForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAuthError();
    const u    = authUsername.value.trim();
    const p    = authPassword.value;
    const role = activeRole;
    const dn   = authDisplayName?.value.trim() || "";
    const sk   = authSkills?.value.trim() || "";
    const hr   = parseFloat(authHours?.value) || 8;

    if (!u || !p) { showAuthError("Please enter your username and password."); return; }

    if (authMode === "login") {
      await performAuth("login", u, p, role);
    } else {
      await performAuth("signup", u, p, role, dn, sk, hr);
    }
  });

  // ─── Auth: Core Login / Register ─────────────────────────────────────────────
  async function performAuth(mode, username, password, role, displayName = "", skills = "", hours = 8) {
    hideAuthError();
    const btnSubmit = document.getElementById("btn-submit-auth");
    btnSubmit.disabled = true;

    try {
      let res, data;

      if (mode === "login") {
        res = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password, role }),
        });
      } else {
        const dn = displayName || username;
        res = await fetch("/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password, role, display_name: dn, skills, hours }),
        });
      }

      data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data.detail || "Authentication failed. Check your credentials.");
      }

      applyUserSession(data, username, password);
      showToast(`Welcome${mode === "signup" ? " aboard" : " back"}, ${data.display_name}! 🎉`);

    } catch (err) {
      showAuthError(err.message);
    } finally {
      btnSubmit.disabled = false;
    }
  }

  // ─── Session: Apply Authenticated User State ──────────────────────────────────
  function applyUserSession(user, username, password) {
    currentUser = user;
    currentCredentials = { username: user.username || username, password };

    // Header pill
    headerUserAvatar.textContent = user.display_name.charAt(0).toUpperCase();
    headerUserName.textContent   = user.display_name;
    headerUserRole.textContent   = user.role === "lead" ? "👑 Team Lead" : "👤 Candidate";

    // Close modal
    loginModal.classList.add("hidden");

    if (user.role === "lead") {
      showLeadDashboard(user);
    } else {
      showCandidateDashboard(user);
    }
  }

  // ─── Lead Dashboard ───────────────────────────────────────────────────────────
  function showLeadDashboard(user) {
    leadView.classList.remove("hidden");
    candidateView.classList.add("hidden");
    resultsSection.classList.add("hidden");

    headerBadgeRole.textContent = "TEAM COORDINATOR";
    headerLeadDesc.textContent  =
      "Automated workload balancing, fairness scoring, and conflict-free assignment engine for hackathon teams.";

    // Pre-fill saved team data if available
    const dd = user.dashboard_data || {};
    if (dd.members && dd.members.length > 0) {
      membersTbody.innerHTML = "";
      dd.members.forEach(m => membersTbody.appendChild(createMemberRow(m)));
    }
    if (dd.tasks && dd.tasks.length > 0) {
      tasksTbody.innerHTML = "";
      dd.tasks.forEach(t => tasksTbody.appendChild(createTaskRow(t)));
    }

    // Re-render last schedule if saved
    if (dd.latest_schedule) {
      latestCoordinationResult = dd.latest_schedule;
      renderLeadResults(dd.latest_schedule, false);
    }
  }

  // ─── Candidate Dashboard ──────────────────────────────────────────────────────
  function showCandidateDashboard(user) {
    leadView.classList.add("hidden");
    candidateView.classList.remove("hidden");
    resultsSection.classList.add("hidden");

    headerBadgeRole.textContent = "MY WORKSPACE";
    headerLeadDesc.textContent  =
      `Personalized workload hub for ${user.display_name} — view your assigned tasks, AI rationale, and team sprint status.`;

    // Fill profile card
    candAvatar.textContent      = user.display_name.charAt(0).toUpperCase();
    candDisplayName.textContent = user.display_name;
    candSkills.textContent      = `Skills: ${user.skills || "General Development"}`;
    candHours.textContent       = `Capacity: ${user.hours || 8}h`;

    const dd = user.dashboard_data || {};
    candBio.textContent    = dd.bio    || `Registered candidate — ${user.skills || "General Development"}.`;
    candStatus.textContent = `● ${dd.status || "Active in Sprint"}`;

    // Load shared team schedule
    const sched = dd.shared_schedule || dd.latest_schedule || null;
    renderCandidateTasks(user, sched);
  }

  function renderCandidateTasks(user, sched) {
    candidateGrid.innerHTML = "";

    if (!sched || !sched.assignments || sched.assignments.length === 0) {
      candTeamSummary.textContent =
        "No schedule has been generated by your Team Lead yet. Check back soon!";
      candAssignedHours.textContent = "0h";
      const notice = document.createElement("div");
      notice.className = "card";
      notice.style.cssText = "grid-column:1/-1;text-align:center;padding:2rem;";
      notice.textContent = "Awaiting coordinator schedule from your Team Lead…";
      candidateGrid.appendChild(notice);
      return;
    }

    // Team summary
    candTeamSummary.textContent =
      sched.executive_summary || "Team schedule loaded from coordinator.";

    const firstName   = user.display_name.split(" ")[0].toLowerCase();
    const displayLow  = user.display_name.toLowerCase();
    let myHours = 0, myCount = 0;

    sched.assignments.forEach((item, idx) => {
      const assigneeLow = item.assigned_to.toLowerCase();
      const isMine = assigneeLow.includes(firstName) || assigneeLow.includes(displayLow);
      if (isMine) { myHours += item.estimated_hours || 0; myCount++; }

      const card = buildTaskCard(item, idx, isMine, true);
      candidateGrid.appendChild(card);
    });

    candAssignedHours.textContent = myCount > 0 ? `${myHours}h` : "0h";

    if (myCount === 0) {
      const notice = document.createElement("div");
      notice.className = "card";
      notice.style.cssText = "grid-column:1/-1;text-align:center;padding:2rem;";
      notice.textContent = "No tasks are currently assigned to you in the latest schedule.";
      candidateGrid.appendChild(notice);
    }
  }

  // ─── Lead Results Rendering ───────────────────────────────────────────────────
  function renderLeadResults(data, animate = true) {
    latestCoordinationResult = data;
    resultsSection.classList.remove("hidden");

    if (animate) {
      resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
      animateCountUp(data.fairness_score);
    } else {
      scoreValue.textContent = data.fairness_score;
    }

    executiveSummaryText.textContent = data.executive_summary;
    metaEngineMode.textContent       = data.is_mock ? "Offline Engine" : "OpenRouter AI";

    renderAssignmentsGrid(data, assignmentsGrid);
  }

  function renderAssignmentsGrid(data, grid) {
    grid.innerHTML = "";
    const user = currentUser;
    const firstName  = user ? user.display_name.split(" ")[0].toLowerCase() : "";
    const displayLow = user ? user.display_name.toLowerCase() : "";

    let filteredList = data.assignments;
    if (activeFilter === "my" && user) {
      filteredList = data.assignments.filter(item => {
        const al = item.assigned_to.toLowerCase();
        return al.includes(firstName) || al.includes(displayLow);
      });
    }

    if (filteredList.length === 0) {
      const notice = document.createElement("div");
      notice.className = "card";
      notice.style.cssText = "grid-column:1/-1;text-align:center;padding:2rem;";
      notice.textContent = "No tasks match this filter.";
      grid.appendChild(notice);
      return;
    }

    filteredList.forEach((item, idx) => {
      const isMine = user && (() => {
        const al = item.assigned_to.toLowerCase();
        return al.includes(firstName) || al.includes(displayLow);
      })();
      grid.appendChild(buildTaskCard(item, idx, isMine, false));
    });
  }

  // ─── Shared Task Card Builder ─────────────────────────────────────────────────
  function buildTaskCard(item, index, isMine, isCandidateView) {
    const card = document.createElement("div");
    card.className = "task-card";
    card.style.setProperty("--index", index);
    if (isMine) card.classList.add("my-task");

    // Header row
    const header = document.createElement("div");
    header.className = "task-card-header";

    const title = document.createElement("h4");
    title.className = "task-title";
    title.textContent = item.task_title;

    const badgeGroup = document.createElement("div");
    badgeGroup.style.cssText = "display:flex;align-items:center;gap:0.4rem;flex-wrap:wrap;";

    if (isMine) {
      const myBadge = document.createElement("span");
      myBadge.className = "my-task-badge";
      myBadge.textContent = "★ YOUR TASK";
      badgeGroup.appendChild(myBadge);
    }
    const hrBadge = document.createElement("span");
    hrBadge.className = "task-hours-badge";
    hrBadge.textContent = `${item.estimated_hours}h`;
    badgeGroup.appendChild(hrBadge);

    header.appendChild(title);
    header.appendChild(badgeGroup);

    // Assignee row
    const assigneeRow = document.createElement("div");
    assigneeRow.className = "task-assigned-row";

    const avatar = document.createElement("div");
    avatar.className = "assignee-avatar";
    avatar.textContent = item.assigned_to.charAt(0).toUpperCase();

    const info = document.createElement("div");
    info.className = "assignee-info";

    const nameSpan = document.createElement("span");
    nameSpan.className = "assignee-name";
    nameSpan.textContent = item.assigned_to;

    const skillTag = document.createElement("span");
    skillTag.className = "assignee-skill-tag";
    skillTag.textContent = `★ ${item.required_skill}`;

    info.appendChild(nameSpan);
    info.appendChild(skillTag);
    assigneeRow.appendChild(avatar);
    assigneeRow.appendChild(info);

    // Reasoning
    const reasoning = document.createElement("p");
    reasoning.className = "task-reasoning";
    reasoning.textContent = item.reasoning;

    card.appendChild(header);
    card.appendChild(assigneeRow);
    card.appendChild(reasoning);

    return card;
  }

  // ─── Row Builders ─────────────────────────────────────────────────────────────
  function createMemberRow(data = { name: "", skills: "", hours: 8 }) {
    const tr = document.createElement("tr");

    const makeInput = (type, cls, placeholder, value, extra = {}) => {
      const td = document.createElement("td");
      const inp = document.createElement("input");
      inp.type = type; inp.className = `form-control ${cls}`;
      inp.placeholder = placeholder; inp.value = value;
      Object.assign(inp, extra);
      td.appendChild(inp);
      return td;
    };

    tr.appendChild(makeInput("text",   "input-member-name",   "e.g. Alex",       data.name));
    tr.appendChild(makeInput("text",   "input-member-skills", "e.g. React, UI",  data.skills));
    tr.appendChild(makeInput("number", "input-member-hours",  "hrs",             data.hours, { min: 1, max: 168 }));

    const tdDel = document.createElement("td");
    const del = document.createElement("button");
    del.className = "btn-remove"; del.title = "Remove"; del.innerHTML = "×";
    del.addEventListener("click", () => tr.remove());
    tdDel.appendChild(del);
    tr.appendChild(tdDel);
    return tr;
  }

  function createTaskRow(data = { title: "", required_skill: "", hours: 2 }) {
    const tr = document.createElement("tr");

    const makeInput = (type, cls, placeholder, value, extra = {}) => {
      const td = document.createElement("td");
      const inp = document.createElement("input");
      inp.type = type; inp.className = `form-control ${cls}`;
      inp.placeholder = placeholder; inp.value = value;
      Object.assign(inp, extra);
      td.appendChild(inp);
      return td;
    };

    tr.appendChild(makeInput("text",   "input-task-title", "e.g. Build Landing Page", data.title));
    tr.appendChild(makeInput("text",   "input-task-skill", "e.g. Frontend",           data.required_skill));
    tr.appendChild(makeInput("number", "input-task-hours", "hrs",                     data.hours, { min: 0.5, max: 100, step: 0.5 }));

    const tdDel = document.createElement("td");
    const del = document.createElement("button");
    del.className = "btn-remove"; del.title = "Remove"; del.innerHTML = "×";
    del.addEventListener("click", () => tr.remove());
    tdDel.appendChild(del);
    tr.appendChild(tdDel);
    return tr;
  }

  // ─── Sample Data Loader ───────────────────────────────────────────────────────
  function loadSampleData() {
    membersTbody.innerHTML = "";
    tasksTbody.innerHTML   = "";

    const members = [...BASE_SAMPLE_MEMBERS];
    const tasks   = [...BASE_SAMPLE_TASKS];

    // Include logged-in candidate in roster if they're a candidate
    if (currentUser && currentUser.role === "candidate") {
      const already = members.some(m => m.name.toLowerCase().includes(currentUser.display_name.split(" ")[0].toLowerCase()));
      if (!already) {
        members.push({
          name:   currentUser.display_name,
          skills: currentUser.skills || "General Development",
          hours:  currentUser.hours  || 8,
        });
      }
    }

    members.forEach(m => membersTbody.appendChild(createMemberRow(m)));
    tasks.forEach(t   => tasksTbody.appendChild(createTaskRow(t)));
    showToast("⚡ Sample hackathon data loaded!");
    hideError();
  }

  // ─── Coordinate / Generate Schedule ──────────────────────────────────────────
  async function handleCoordinate() {
    hideError();

    const memberRows = membersTbody.querySelectorAll("tr");
    const taskRows   = tasksTbody.querySelectorAll("tr");

    const members = [];
    memberRows.forEach(r => {
      const name   = r.querySelector(".input-member-name")?.value.trim();
      const skills = r.querySelector(".input-member-skills")?.value.trim();
      const hours  = parseFloat(r.querySelector(".input-member-hours")?.value) || 1;
      if (name && skills) members.push({ name, skills, hours });
    });

    const tasks = [];
    taskRows.forEach(r => {
      const title          = r.querySelector(".input-task-title")?.value.trim();
      const required_skill = r.querySelector(".input-task-skill")?.value.trim() || "General";
      const estimated_hours = parseFloat(r.querySelector(".input-task-hours")?.value) || 1;
      if (title) tasks.push({ title, required_skill, estimated_hours });
    });

    if (!members.length || !tasks.length) {
      showToast("Add at least 1 member and 1 task, or click ⚡ Load Sample Hackathon Data.");
      return;
    }

    btnGenerate.classList.add("loading");
    btnGenerate.disabled = true;

    try {
      const res = await fetch("/api/coordinate", {
        method: "POST",
        headers: getAuthenticatedHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({ members, tasks }),
      });

      const result = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(result.detail || `Server error (${res.status})`);

      metaMemberCount.textContent = `${members.length} Teammates`;
      metaTaskCount.textContent   = `${tasks.length} Tasks Allocated`;

      renderLeadResults(result, true);
      showToast("✅ Schedule generated and shared with candidates!");

    } catch (err) {
      showError("Coordination Failed", err.message);
    } finally {
      btnGenerate.classList.remove("loading");
      btnGenerate.disabled = false;
    }
  }

  // ─── Animated Count-Up ────────────────────────────────────────────────────────
  function animateCountUp(target) {
    const duration = 1200;
    const start    = performance.now();
    function step(now) {
      const progress = Math.min((now - start) / duration, 1);
      const ease     = 1 - Math.pow(1 - progress, 3);
      scoreValue.textContent = Math.floor(ease * target);
      if (progress < 1) requestAnimationFrame(step);
      else scoreValue.textContent = target;
    }
    requestAnimationFrame(step);
  }

  // ─── Filter Buttons (Lead View) ───────────────────────────────────────────────
  const filterBtnAll = document.getElementById("filter-btn-all");
  const filterBtnMy  = document.getElementById("filter-btn-my");

  if (filterBtnAll) {
    filterBtnAll.addEventListener("click", () => {
      activeFilter = "all";
      filterBtnAll.classList.add("active");
      filterBtnMy.classList.remove("active");
      if (latestCoordinationResult) renderAssignmentsGrid(latestCoordinationResult, assignmentsGrid);
    });
  }
  if (filterBtnMy) {
    filterBtnMy.addEventListener("click", () => {
      activeFilter = "my";
      filterBtnMy.classList.add("active");
      filterBtnAll.classList.remove("active");
      if (latestCoordinationResult) renderAssignmentsGrid(latestCoordinationResult, assignmentsGrid);
    });
  }

  // ─── Health Check ─────────────────────────────────────────────────────────────
  async function checkHealth() {
    try {
      const res  = await fetch("/api/health");
      const data = await res.json();
      engineStatusText.textContent = data.mock_mode
        ? "Engine: Mock Mode (Offline Ready)"
        : "Engine: OpenRouter API Active";
    } catch {
      engineStatusText.textContent = "Engine: Local Backend";
    }
  }

  // ─── Event Bindings ───────────────────────────────────────────────────────────
  btnSwitchUser.addEventListener("click", () => {
    currentCredentials = null;
    loginModal.classList.remove("hidden");
    setAuthMode("login");
    setActiveRole("lead");
  });

  btnAddMember.addEventListener("click", () => membersTbody.appendChild(createMemberRow()));
  btnAddTask.addEventListener("click",   () => tasksTbody.appendChild(createTaskRow()));
  btnLoadSample.addEventListener("click", loadSampleData);
  btnGenerate.addEventListener("click",  handleCoordinate);
  btnRetry.addEventListener("click",     handleCoordinate);

  // ─── Boot Sequence ────────────────────────────────────────────────────────────
  setActiveRole("lead");
  setAuthMode("login");

  // Seed empty rows (Lead view starts with empty form)
  membersTbody.appendChild(createMemberRow({ name: "", skills: "", hours: 10 }));
  tasksTbody.appendChild(createTaskRow({ title: "", required_skill: "", hours: 3 }));

  checkHealth();

  // Show modal on load — force proper auth, no auto-login
  loginModal.classList.remove("hidden");

});
