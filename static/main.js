const ws = new WebSocket("ws://localhost:8766");

ws.onopen = () => {
  console.log("Connected to server at ws://localhost:8766");
};

ws.onmessage = (event) => {
  let parsed_data;
  try {
    parsed_data = JSON.parse(event.data);  
    console.log(parsed_data)
    if (typeof parsed_data == 'object' && parsed_data !== null && parsed_data["market_code"] == 'REG') {
        updateTable(parsed_data)
    } 
  } catch (error) {
    console.error("Error parsing WebSocket message:", error);
  }
};

// ------------------------------------------------------------------------
const LOCAL_STORAGE_KEY = "selected_columns";
function toggleColumnOptions() {
  console.log("toggle column called")
  const options = document.getElementById("columnOptions");
  options.style.display = options.style.display === "none" ? "block" : "none";
}

function generateColumnOptions() {
  const container = document.getElementById("columnOptions");
  container.innerHTML = ""; // Clear previous options

  columnConfig.forEach((column) => {
    const div = document.createElement("div")
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = column.id;
    checkbox.checked = column.visible;

    const label = document.createElement("label");
    div.appendChild(label)
    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(` ${column.label}`));

    const br = document.createElement("br");

    container.appendChild(label);
    container.appendChild(br);
  });

  const applyButton = document.createElement("button");
  applyButton.textContent = "Apply";
  applyButton.onclick = applyColumns;
  container.appendChild(applyButton);
}

function applyColumns() {
  const checkboxes = document.querySelectorAll("#columnOptions input[type='checkbox']");
  const selectedColumns = Array.from(checkboxes).filter((cb) => cb.checked).map((cb) => cb.value);

  // Update the visibility in columnConfig
  columnConfig.forEach((column) => {
    column.visible = selectedColumns.includes(column.id);
  });

  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(selectedColumns));
  renderTable(); // Re-render the table with updated columns
}

function loadColumns() {
  console.log('loaded columns')
  const selectedColumns = JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY)) || [];
  columnConfig.forEach((column) => {
    column.visible = selectedColumns.length === 0 || selectedColumns.includes(column.id);
  });

  generateColumnOptions();
  renderTable();
}
function generateStockOptions() {
  const container = document.getElementById("stockOptions");
  container.innerHTML = ""; // Clear previous options

  initialData.forEach((stock) => {
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = stock.symbol_code;
    checkbox.checked = stock.visible;

    const label = document.createElement("label");
    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(`${stock.label}`));

    const br = document.createElement("br");

    container.appendChild(label);
    container.appendChild(br);
  });

  const applyButton = document.createElement("button");
  applyButton.textContent = "Apply";
  applyButton.onclick = applyStocks;
  container.appendChild(applyButton);
}
// ------------------------------------------------------------------------
const LOCAL_STORAGE_STOCKS_KEY = "selected_stocks";
const defaultStocks = ["MARI", "AGTL", "PSO"];
const tableBody = document.getElementById("table-body");

// Centralized row configuration
let rowConfig = []; // This will store all stock rows

// Initialize with initial data from the database
function initializeRowConfig(initialData) {
  console.log('init row conf is called with data: ', initialData)

  rowConfig = initialData.map((row) => ({
    ...row,
    visible: false, // Controls visibility of rows
  }));
}
// Update rowConfig dynamically (e.g., from WebSocket or filters)
function updateRowConfig(newRows) {
  newRows.forEach((newRow) => {
    const existingRowIndex = rowConfig.findIndex((row) => row.symbol_code === newRow.symbol_code);
    if (existingRowIndex >= 0) {
      // Update existing stock
      rowConfig[existingRowIndex] = { ...rowConfig[existingRowIndex], ...newRow };
    } else {
      // Add new stock
      rowConfig.push({ ...newRow, visible: true });
    }
  });
}

// Filter stocks based on conditions
function filterRowConfig(conditionFn) {
  rowConfig.forEach((row) => {
    row.visible = conditionFn(row);
  });
}


// Render the table based on rowConfig
function renderTable() {
  console.log('render table form test called')
  const tableHead = document.querySelector("#market-data-table thead tr");
  const tableBody = document.querySelector("#market-data-table tbody");

  // Render headers
  tableHead.innerHTML = "";
  columnConfig
    .filter((column) => column.visible)
    .forEach((column) => {
      const th = document.createElement("th");
      th.textContent = column.label;
      tableHead.appendChild(th);
    });

  // Render rows
  tableBody.innerHTML = "";
  console.log(rowConfig, "from inside render")
  rowConfig.forEach((row) => {
    if (row.visible == true) {
      const tr = document.createElement("tr");
      tr.setAttribute("data-symbol", row.symbol_code);

      columnConfig
        .filter((column) => column.visible)
        .forEach((column) => {
          const td = document.createElement("td");
          td.textContent = row[column.id] || "";
          td.classList.add(column.id)
          tr.appendChild(td);
        });

      tableBody.appendChild(tr);
    }
    else{
      console.log('visibility is false')
    }
  });
}
function toggleStockOptions() {
  console.log("toggle stock called");
  const options = document.getElementById("stockOptions");
  options.style.display = options.style.display === "none" ? "block" : "none";
}
function populateStockCheckboxes() {
  console.log("Populating stock checkboxes with rowConfig:", rowConfig);
  const checkboxesContainer = document.getElementById("stockCheckboxContainer");

  // Ensure the container exists
  if (!checkboxesContainer) {
    console.error("Element 'stockCheckboxContainer' not found.");
    return;
  }

  checkboxesContainer.innerHTML = ""; // Clear previous checkboxes

  // Populate checkboxes
  rowConfig.forEach((row) => {
    const label = document.createElement("label");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = row.symbol_code;

    // Set the checkbox state based on localStorage
    const selectedStocks = JSON.parse(localStorage.getItem(LOCAL_STORAGE_STOCKS_KEY)) || [];
    checkbox.checked = selectedStocks.includes(row.symbol_code);

    const symbolText = row.symbol_code || "Unknown Symbol"; // Fallback for undefined values
    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(` ${symbolText}`));

    const br = document.createElement("br");
    checkboxesContainer.appendChild(label);
    checkboxesContainer.appendChild(br);
  });
}

function applyStocks() {
  const checkboxes = document.querySelectorAll("#stockCheckboxContainer input[type='checkbox']");
  const selectedStocks = Array.from(checkboxes).filter((cb) => cb.checked).map((cb) => cb.value);

  // Save selected stocks to localStorage
  localStorage.setItem(LOCAL_STORAGE_STOCKS_KEY, JSON.stringify(selectedStocks));

  // Update the visibility of rows in rowConfig based on selected stocks
  rowConfig.forEach((row) => {
    row.visible = selectedStocks.includes(row.symbol_code);
  });

  console.log("Selected stocks saved:", selectedStocks);

  renderTable(); // Re-render the table with updated stock visibility
}

// Load selected stocks on page load
function loadStocks() {
  console.log('loaded stocks')
  const selectedStocks = JSON.parse(localStorage.getItem(LOCAL_STORAGE_STOCKS_KEY)) || defaultStocks;
  // filterRowConfig((row) => selectedStocks.includes(row.symbol_code));
  rowConfig.forEach((row) => {
    row.visible = selectedStocks.includes(row.symbol_code)
  })
  // generateStockOptions()

  populateStockCheckboxes();
  renderTable();
}

  function renderTableHeaders() {
    console.log('render table header is called')
    const tableHeader = document.getElementById("table-header");

      tableHeader.innerHTML = ""; // Clear existing headers

      columnConfig.filter((column) => column.visible).forEach((col) => {
          const th = document.createElement("th");
          th.setAttribute("data-column", col.id);
          th.textContent = col.label;
          tableHeader.appendChild(th);
          th.classList.add("updated-cell");

      });
  }

document.addEventListener("DOMContentLoaded", () => {
  loadColumns();
  loadStocks();
  renderTableHeaders();
  initializeRowConfig(initialData);
});

// Handle WebSocket updates
// function updateTable(data) {
//   const tableBody = document.querySelector("#market-data-table tbody");
//   console.log("updateTable is called");

//   const existingRow = document.querySelector(`tr[data-symbol="${data["symbol_code"]}"]`);
//   if (existingRow) {
//       console.log("Updating existing row");
//       columnConfig.filter((column) => column.visible).forEach((col, index) => {
//           const cell = existingRow.cells[index];
//           if (data[col.id] !== undefined && cell) {
//               cell.textContent = data[col.id];

//               cell.classList.add("updated-cell");
//               setTimeout(() => cell.classList.remove("updated-cell"), 5000); // Remove class after 1 second
//               console.log('added the class')

//           }
//       });
//   } else {
//       console.log("Adding new row");
//       initializeRowConfig(data)
//       const newRow = document.createElement("tr");
//       newRow.setAttribute("data-symbol", data["symbol_code"]);

//       columnConfig .filter((column) => column.visible).forEach((col) => {
//           const td = document.createElement("td");
//           td.textContent = data[col.id] || "";
//           newRow.appendChild(td);
//           td.classList.add("updated-cell");
//           setTimeout(() => td.classList.remove("updated-cell"), 5000); // Remove class after 1 second
//           console.log('added the class')
//       });

//       tableBody.appendChild(newRow);
//   }
// }
function updateTable(data) {
  const tableBody = document.querySelector("#market-data-table tbody");
  console.log("updateTable is called");

  const existingRow = document.querySelector(`tr[data-symbol="${data["symbol_code"]}"]`);
  if (existingRow) {
      console.log("Updating existing row");
      columnConfig.filter((column) => column.visible).forEach((col, index) => {
          const cell = existingRow.cells[index];
          if (data[col.id] !== undefined && cell) {
              let previousValue = parseFloat(cell.textContent) || 0;
              let newValue = parseFloat(data[col.id]);

              cell.textContent = data[col.id]; // Update the value
              cell.classList.add(col.id)
              // Determine flash color
              if (newValue > previousValue) {
                  cell.classList.add("flash-green");
              } else if (newValue < previousValue) {
                  cell.classList.add("flash-red");
              }

              // Remove flash effect after 500ms
              setTimeout(() => {
                  cell.classList.remove("flash-green", "flash-red");
              }, 500);
          }
      });
  } else {
      console.log("Adding new row");
      initializeRowConfig(data);
      const newRow = document.createElement("tr");
      newRow.setAttribute("data-symbol", data["symbol_code"]);

      columnConfig.filter((column) => column.visible).forEach((col) => {
          const td = document.createElement("td");
          td.textContent = data[col.id] || "";
          td.classList.add(col.id)
          newRow.appendChild(td);
      });

      tableBody.appendChild(newRow);
  }
}


ws.onclose = () => {
  console.log("Connection to server closed.");
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
} 