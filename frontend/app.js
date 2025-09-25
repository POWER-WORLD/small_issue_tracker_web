(() => {
	const API = (path) => `${window.API_BASE || 'http://127.0.0.1:8000'}${path}`;

	const els = {
		search: document.getElementById('search'),
		searchBtn: document.getElementById('searchBtn'),
		status: document.getElementById('statusFilter'),
		priority: document.getElementById('priorityFilter'),
		assignee: document.getElementById('assigneeFilter'),
		clear: document.getElementById('clearFilters'),
		tableBody: document.querySelector('#issuesTable tbody'),
		pageInfo: document.getElementById('pageInfo'),
		prev: document.getElementById('prevPage'),
		next: document.getElementById('nextPage'),
		pageSize: document.getElementById('pageSize'),
		createBtn: document.getElementById('createIssueBtn'),
		modal: document.getElementById('modal'),
		modalTitle: document.getElementById('modalTitle'),
		formTitle: document.getElementById('formTitle'),
		formDescription: document.getElementById('formDescription'),
		formStatus: document.getElementById('formStatus'),
		formPriority: document.getElementById('formPriority'),
		formAssignee: document.getElementById('formAssignee'),
		saveIssue: document.getElementById('saveIssue'),
		cancelModal: document.getElementById('cancelModal'),
		drawer: document.getElementById('drawer'),
		detailJson: document.getElementById('detailJson'),
		closeDrawer: document.getElementById('closeDrawer'),
	};

	const state = {
		page: 1,
		pageSize: parseInt(els.pageSize.value, 10),
		sortBy: 'updatedAt',
		sortDir: 'desc',
		search: '',
		status: '',
		priority: '',
		assignee: '',
		editId: null,
		total: 0,
	};

	async function fetchIssues() {
		const params = new URLSearchParams();
		if (state.search) params.set('search', state.search);
		if (state.status) params.set('status', state.status);
		if (state.priority) params.set('priority', state.priority);
		if (state.assignee) params.set('assignee', state.assignee);
		params.set('sortBy', state.sortBy);
		params.set('sortDir', state.sortDir);
		params.set('page', String(state.page));
		params.set('pageSize', String(state.pageSize));
		const res = await fetch(API(`/issues?${params.toString()}`));
		if (!res.ok) throw new Error('Failed to load issues');
		return res.json();
	}

	function fmtDate(s) {
		try { return new Date(s).toLocaleString(); } catch { return s; }
	}

	function renderTable(items) {
		els.tableBody.innerHTML = '';
		for (const it of items) {
			const tr = document.createElement('tr');
			tr.innerHTML = `
				<td>${it.id}</td>
				<td>${escapeHtml(it.title)}</td>
				<td>${it.status}</td>
				<td>${it.priority}</td>
				<td>${escapeHtml(it.assignee || '')}</td>
				<td>${fmtDate(it.updatedAt)}</td>
				<td><button data-edit="${it.id}">Edit</button></td>
			`;
			tr.addEventListener('click', (e) => {
				if ((e.target)?.dataset?.edit) return; // do not trigger detail on edit click
				openDetail(it);
			});
			tr.querySelector('button[data-edit]')?.addEventListener('click', () => openEdit(it));
			els.tableBody.appendChild(tr);
		}
	}

	function renderPageInfo() {
		const from = (state.page - 1) * state.pageSize + 1;
		const to = Math.min(state.page * state.pageSize, state.total);
		els.pageInfo.textContent = `${from}-${to} of ${state.total}`;
	}

	async function refresh() {
		const data = await fetchIssues();
		state.total = data.total;
		renderTable(data.items);
		renderPageInfo();
	}

	function applyFilters() {
		state.page = 1;
		state.search = els.search.value.trim();
		state.status = els.status.value;
		state.priority = els.priority.value;
		state.assignee = els.assignee.value.trim();
		refresh();
	}

	function clearFilters() {
		els.search.value = '';
		els.status.value = '';
		els.priority.value = '';
		els.assignee.value = '';
		applyFilters();
	}

	function openCreate() {
		state.editId = null;
		els.modalTitle.textContent = 'Create Issue';
		els.formTitle.value = '';
		els.formDescription.value = '';
		els.formStatus.value = 'open';
		els.formPriority.value = 'medium';
		els.formAssignee.value = '';
		els.modal.classList.remove('hidden');
	}

	function openEdit(it) {
		state.editId = it.id;
		els.modalTitle.textContent = 'Edit Issue';
		els.formTitle.value = it.title || '';
		els.formDescription.value = it.description || '';
		els.formStatus.value = it.status || 'open';
		els.formPriority.value = it.priority || 'medium';
		els.formAssignee.value = it.assignee || '';
		els.modal.classList.remove('hidden');
	}

	function closeModal() { els.modal.classList.add('hidden'); }

	async function save() {
		const body = {
			title: els.formTitle.value.trim(),
			description: els.formDescription.value.trim() || null,
			status: els.formStatus.value,
			priority: els.formPriority.value,
			assignee: els.formAssignee.value.trim() || null,
		};
		if (!body.title) { alert('Title is required'); return; }
		if (state.editId == null) {
			const res = await fetch(API('/issues'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
			if (!res.ok) { alert('Failed to create'); return; }
		} else {
			const res = await fetch(API(`/issues/${state.editId}`), { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
			if (!res.ok) { alert('Failed to update'); return; }
		}
		closeModal();
		refresh();
	}

	function openDetail(it) {
		els.detailJson.textContent = JSON.stringify(it, null, 2);
		els.drawer.classList.remove('hidden');
	}
	function closeDetail() { els.drawer.classList.add('hidden'); }

	function onSort(th) {
		const key = th.dataset.sort;
		if (!key) return;
		if (state.sortBy === key) {
			state.sortDir = state.sortDir === 'asc' ? 'desc' : 'asc';
		} else {
			state.sortBy = key;
			state.sortDir = 'asc';
		}
		refresh();
	}

	function setupSort() {
		for (const th of document.querySelectorAll('#issuesTable thead th[data-sort]')) {
			th.addEventListener('click', () => onSort(th));
		}
	}

	function escapeHtml(s) {
		return s?.replace(/[&<>"]+/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])) || '';
	}

	// Events
	els.searchBtn.addEventListener('click', applyFilters);
	els.clear.addEventListener('click', clearFilters);
	els.prev.addEventListener('click', () => { if (state.page > 1) { state.page--; refresh(); } });
	els.next.addEventListener('click', () => { if (state.page * state.pageSize < state.total) { state.page++; refresh(); } });
	els.pageSize.addEventListener('change', () => { state.pageSize = parseInt(els.pageSize.value, 10); state.page = 1; refresh(); });
	els.createBtn.addEventListener('click', openCreate);
	els.cancelModal.addEventListener('click', closeModal);
	els.saveIssue.addEventListener('click', save);
	els.closeDrawer.addEventListener('click', closeDetail);

	setupSort();
	refresh();
})();
