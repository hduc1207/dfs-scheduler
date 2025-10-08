// ----------------------------
// CẤU HÌNH
// ----------------------------
const specialties = {
  "Nội tổng quát": { "Bác sĩ An": ["Bác sĩ Bình"], "Bác sĩ Bình": [] },
  "Tim mạch": { "Bác sĩ Chi": ["Bác sĩ Dũng"], "Bác sĩ Dũng": [] },
  "Tai Mũi Họng": { "Bác sĩ Hạnh": ["Bác sĩ Khôi"], "Bác sĩ Khôi": [] }
};

const quyTrinh = [
  ["Nội tổng quát", "Tim mạch", "Tai Mũi Họng"],
  ["Tim mạch", "Nội tổng quát"],
  ["Tai Mũi Họng"]
];

const colors = {
  "Nội tổng quát": "border-blue-500",
  "Tim mạch": "border-green-500",
  "Tai Mũi Họng": "border-purple-500"
};

const examDuration = 30; // phút
let schedules = {};
Object.values(specialties).forEach(sp => {
  Object.keys(sp).forEach(doc => schedules[doc] = []);
});
let allAppointments = [];

// ----------------------------
// DFS TÌM BÁC SĨ RẢNH
// ----------------------------
function dfsFindDoctor(graph, doctor, visited, time) {
  if (visited.has(doctor)) return null;
  visited.add(doctor);

  const schedule = schedules[doctor] || [];
  const isFree = schedule.every(([s, e]) => !(s <= time && time < e));

  if (isFree) return doctor;

  for (const nextDoc of graph[doctor]) {
    const result = dfsFindDoctor(graph, nextDoc, visited, time);
    if (result) return result;
  }
  return null;
}

// ----------------------------
// ĐẶT LỊCH KHÁM
// ----------------------------
function dfsScheduleProcess(name, process, startTime, isEmergency) {
  const result = [];
  let currentTime = new Date(startTime);

  for (const specialty of process) {
    const doctors = specialties[specialty];
    const firstDoctor = Object.keys(doctors)[0];
    const assigned = dfsFindDoctor(doctors, firstDoctor, new Set(), currentTime);

    if (assigned) {
      const endTime = new Date(currentTime.getTime() + examDuration * 60000);
      schedules[assigned].push([currentTime, endTime]);
      result.push({ specialty, doctor: assigned, start: currentTime, end: endTime });
      allAppointments.push({ name, specialty, doctor: assigned, start: currentTime, end: endTime, emergency: isEmergency });
      currentTime = endTime;
    } else {
      result.push({ specialty, doctor: "Không có bác sĩ trống", start: "", end: "" });
    }
  }
  return result;
}

// ----------------------------
// XỬ LÝ GIAO DIỆN
// ----------------------------
function schedulePatient() {
  const name = document.getElementById("name").value.trim();
  const processIndex = parseInt(document.getElementById("process").value);
  const start = document.getElementById("start").value;
  const status = document.getElementById("status").value;

  if (!name || !start) {
    alert("⚠️ Vui lòng nhập đầy đủ thông tin!");
    return;
  }

  const isEmergency = (status === "capcuu");
  const lich = dfsScheduleProcess(name, quyTrinh[processIndex], start, isEmergency);

  const resultDiv = document.getElementById("result");
  let html = `
    <div class="bg-white shadow-xl rounded-xl p-6 border-t-4 ${isEmergency ? 'border-red-500' : 'border-blue-500'} animate-fadeIn">
      <h2 class="text-xl font-bold text-blue-700 mb-4">📋 Lịch khám của ${name} ${isEmergency ? '(Cấp cứu)' : ''}</h2>
  `;

  lich.forEach(item => {
    if (item.doctor !== "Không có bác sĩ trống") {
      html += `
        <div class="border-l-4 ${colors[item.specialty]} pl-3 mb-3">
          <b>${item.specialty}</b><br>
          👨‍⚕️ ${item.doctor}<br>
          🕒 ${item.start.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
          → ${item.end.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
        </div>`;
    } else {
      html += `
        <div class="border-l-4 border-red-500 pl-3 mb-3 bg-red-50">
          <b>${item.specialty}</b><br>
          ❌ Không có bác sĩ trống tại thời điểm này
        </div>`;
    }
  });

  html += `</div>`;
  resultDiv.innerHTML = html;
}

// ----------------------------
// HIỂN THỊ TOÀN BỘ LỊCH BÁC SĨ
// ----------------------------
function showAllSchedules() {
  const resultDiv = document.getElementById("result");
  let html = `<div class="bg-white shadow-xl rounded-xl p-6 border-t-4 border-green-500 animate-fadeIn">`;
  html += `<h2 class="text-xl font-bold text-green-700 mb-4">🩻 Lịch làm việc của bác sĩ</h2>`;

  for (const [doctor, appointments] of Object.entries(schedules)) {
    html += `<h3 class="font-semibold text-blue-600 mt-4">${doctor}</h3>`;
    if (appointments.length === 0) {
      html += `<p class="text-gray-500">Chưa có lịch</p>`;
      continue;
    }
    appointments.sort((a, b) => a[0] - b[0]);
    appointments.forEach(([start, end]) => {
      html += `<div class="ml-3 text-sm text-gray-700">🕒 ${start.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})} → ${end.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</div>`;
    });
  }

  html += `</div>`;
  resultDiv.innerHTML = html;
}

// ----------------------------
// XUẤT FILE EXCEL (CSV)
// ----------------------------
function exportToExcel() {
  if (allAppointments.length === 0) {
    alert("⚠️ Chưa có dữ liệu để xuất!");
    return;
  }
  let csv = "Tên bệnh nhân,Chuyên khoa,Bác sĩ,Giờ bắt đầu,Giờ kết thúc,Tình trạng\n";
  allAppointments.forEach(a => {
    csv += `${a.name},${a.specialty},${a.doctor},${a.start.toLocaleString()},${a.end.toLocaleString()},${a.emergency ? "Cấp cứu" : "Bình thường"}\n`;
  });

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  saveAs(blob, "LichKhamBenh.csv");
}
