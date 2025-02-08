function showSectorFilter(){
  const sectorFilterModal = document.getElementById('sectorFilterModal');
  generateSectorOptions();
  sectorFilterModal.style.display = sectorFilterModal.style.display === "none" ? "block" : "none";
}
function closeSectorFilter() {
  const modal = document.getElementById("sectorFilterModal");
  modal.style.display = "none";
}
function generateSectorOptions() {
  const container = document.getElementById("sectorOptions");
  container.innerHTML = "";

  // Use a Set to store unique sectors
  const uniqueSectors = new Set();

  // Collect unique sectors
  initialData.forEach(stock => {
    uniqueSectors.add(stock.sector);
  });

  // Iterate over the unique sectors to create checkboxes
  uniqueSectors.forEach(sector => {
    if(sector != ""){
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.value = sector;

      // Assuming visibility is a global/default value; adjust as needed
      checkbox.checked = false;

      const label = document.createElement("label");
      label.appendChild(checkbox);
      label.appendChild(document.createTextNode(sector));

      const br = document.createElement("br");
      container.appendChild(label);
      container.appendChild(br);
  }});
}

function applySectorFilter(){
  const checkboxes = document.querySelectorAll("#sectorOptions input[type='checkbox']");
  selectedSectors = Array.from(checkboxes)
    .filter(checkbox => checkbox.checked)
    .map(checkbox => checkbox.value);
  filteredStocks = initialData.filter(stock => selectedSectors.includes(stock.sector))
  console.log(filteredStocks)
}

// function generateSectorOptions() {
//   const container = document.getElementById("sectorOptions");
//   container.innerHTML = ""; // Clear existing content

//   // Create a unique set of sectors
//   const uniqueSectors = Array.from(new Set(initialData.map(stock => stock.sector)));

//   // Create and configure the <select> element
//   const select = Object.assign(document.createElement("select"), {
//     multiple: true,
//     id: "sectorSelect"
//   });

//   // Populate the <select> with unique sector options
//   uniqueSectors.forEach(sector => {
//     select.appendChild(new Option(sector, sector));
//   });

//   // Append the <select> to the container
//   container.appendChild(select);

//   // Create and append a container for displaying selected options
//   const selectedContainer = Object.assign(document.createElement("div"), {
//     id: "selectedSectors",
//     style: "margin-top: 10px;"
//   });
//   container.appendChild(selectedContainer);

//   // Handle selection changes
//   select.addEventListener("change", () => displaySelectedOptions(select));
// }

// // Function to display selected options
// function displaySelectedOptions(select) {
//   const selectedContainer = document.getElementById("selectedSectors");
//   selectedContainer.innerHTML = ""; // Clear previous selections

//   // Get all selected options
//   const selectedOptions = Array.from(select.selectedOptions);

//   // Display selected options
//   if (selectedOptions.length > 0) {
//     selectedOptions.forEach(option => {
//       const div = document.createElement("div");

//       div.textContent = option.value;
//       selectedContainer.appendChild(div);
//     });
//   } else {
//     selectedContainer.textContent = "No sectors selected";
//   }
// }
