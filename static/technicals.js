function showTechnicalOptions() {
  const technicalOptions = document.getElementById("technicalOptions");
  technicalOptions.style.display = "block";

  // Show initial options (RSI and SMA)
  const rsiOption = document.getElementById("rsiOption");
  const smaOption = document.getElementById("smaOption");

  rsiOption.style.display = "block";
  smaOption.style.display = "block";
}
function saveColumnConfig() {
  const visibleColumns = columnConfig.filter((col) => col.visible).map((col) => col.id);
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(visibleColumns));
}
function addStocks(newStocks) {
  newStocks.forEach((stock) => {
    // Add the stock to the table
    renderRow(stock);
  });

  // Recompute all technicals for the new rows
  columnConfig.forEach((column) => {
    if (column.id.startsWith("sma_") || column.id.startsWith("rsi_")) {
      const [type, timePeriod] = column.id.split("_");
      if (type === "sma") {
        applySMA(timePeriod);
      } else if (type === "rsi") {
        applyRSI(timePeriod);
      }
    }
  });}


function loadColumns() {
  console.log('Loading columns...');
  const savedColumns = JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY)) || [];

  // Update the visibility in columnConfig
  columnConfig.forEach((column) => {
    column.visible = savedColumns.length === 0 || savedColumns.includes(column.id);
  });

  // Re-render table and column options
  generateColumnOptions();
  renderTable();

  // Recompute technicals for visible columns
  columnConfig.forEach((column) => {
    if (column.id.startsWith("sma_") || column.id.startsWith("rsi")) {
      const [type, timePeriod] = column.id.split("_");
      if (type === "sma") {
        applySMA(timePeriod); // Reapply SMA logic
      } else if (type === "rsi") {
        applyRSI(timePeriod); // Reapply RSI logic
      }
    }
  });
}
function applySMA() {
  const smaTimePeriod = document.getElementById("smaTimePeriod").value;
  const smaTimeInterval = document.getElementById("smaTimeInterval").value;
  const smaColumnId = `sma_${smaTimePeriod}`; // Unique ID for the SMA column

  fetch('/apply_technical_indicator', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      indicator: 'sma',
      smaTimePeriod: smaTimePeriod,
      smaTimeInterval: smaTimeInterval,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      const smaData = data.sma_results;

      // Add SMA column to `columnConfig` if it doesn't exist
      if (!columnConfig.some((col) => col.id === smaColumnId)) {
        columnConfig.push({
          id: smaColumnId,
          label: `SMA ${smaTimePeriod}`,
          visible: true,
          editable: false,
        });
        saveColumnConfig(); // Persist changes
      }

      // Update SMA values for all rows
      updateTechnicalData(smaData, smaColumnId, `sma${smaTimePeriod}`);
    })
    .catch((error) => {
      console.error('Error applying SMA:', error);
      alert('Failed to apply SMA');
    });
}

function applyRSI() {
  const rsiInterval = document.getElementById("rsiInterval").value;
  const rsiTimeInterval = document.getElementById("rsiTimeInterval").value;
  
  console.log("RSI Applied with interval: " + rsiInterval + " and time interval: " + rsiTimeInterval);

  // Send data to the backend
  fetch('/apply_technical_indicator', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({
          indicator: 'rsi',
          rsiInterval: rsiInterval,
          rsiTimeInterval: rsiTimeInterval
      })
  })
  .then(response => response.json())
  .then(data => {
      console.log(data.message); // Handle success response from backend
      alert(data.message);
      const rsiData = data.rsi_results;
      console.log(rsiData)

      columnConfig.push({
          "id": "rsi",
          "label": "RSI",
          "visible": true, // Make the RSI column visible
          "editable": false // Optional: make RSI column non-editable
      });
      saveColumnConfig(); // Persist changess
      generateColumnOptions(); // Regenerate options
      renderTableHeaders(); // Re-render table headers to include the new SMA column


      rsiData.forEach((rsiRecord) => {
          // Find the row by symbol_code and update the RSI value
          const row = document.querySelector(`tr[data-symbol="${rsiRecord.symbol_code}"]`);
          if (row) {
              const rsiCell = row.querySelector(`td.rsi`);
              if (rsiCell) {
                  rsiCell.textContent = rsiRecord.rsi;
              } else {
                  // If RSI cell doesn't exist, create one
                  const newCell = document.createElement("td");
                  newCell.classList.add("rsi");
                  newCell.textContent = rsiRecord.rsi;
                  row.appendChild(newCell);
              }
          }
      });
      renderTableHeaders();

  })
  .catch(error => {
      console.error('Error:', error);
      alert('Failed to apply RSI');
  });
}

function updateTechnicalData(technicalData, columnId, valueKey) {
  technicalData.forEach((record) => {
    const row = document.querySelector(`tr[data-symbol="${record.symbol_code}"]`);
    if (row) {
      let cell = row.querySelector(`td.${columnId}`);
      if (!cell) {
        // If the cell doesn't exist, create it
        cell = document.createElement("td");
        cell.classList.add(columnId);
        row.appendChild(cell);
      }
      cell.textContent = record[valueKey];
    }
  });

  renderTableHeaders(); // Re-render table headers to include the new column
}

function backToMainOptions() {
  const rsiOption = document.getElementById("rsiOption");
  const smaOption = document.getElementById("smaOption");
  const technicalOptions = document.getElementById("technicalOptions")
  rsiOption.style.display = "none";
  smaOption.style.display = "none";
  technicalOptions.style.display = "none";

}
