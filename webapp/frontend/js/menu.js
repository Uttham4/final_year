const saveStudentIdToLocalStorage = () => {
    const studentId = document.getElementById("student-id").value;
    localStorage.setItem("currentStudentID", studentId);
    // loadCurrentMenu();
    location.reload();

}

const closeStudentID = () => {
    document.getElementById("student-input-modal").classList.add("hidden");
    document.getElementById("current-menu-container").classList.remove("hidden");
}

let current_menu_list = {};
let totalCost = 0;
let current_menu_list_totalCost = 0; // New variable to track cost of current_menu_list

document.addEventListener("DOMContentLoaded", function () {
    const menuData = {
        Monday: { Morning: ["Pancakes", "Omelette"], Afternoon: ["Rice & Curry", "Salad"], Night: ["Pizza", "Soup"] },
        Tuesday: { Morning: ["Cereal", "Fruits"], Afternoon: ["Pasta", "Garlic Bread"], Night: ["Grilled Chicken", "Veggies"] },
        Wednesday: { Morning: ["French Toast", "Milk"], Afternoon: ["Biryani", "Raita"], Night: ["Burger", "Fries"] },
        Thursday: { Morning: ["Poha", "Tea"], Afternoon: ["Chapati & Dal"], Night: ["Fish Curry", "Rice"] },
        Friday: { Morning: ["Smoothie", "Sandwich"], Afternoon: ["Noodles", "Spring Rolls"], Night: ["BBQ", "Mashed Potatoes"] },
        Saturday: { Morning: ["Idli", "Sambhar"], Afternoon: ["Pulao", "Curd"], Night: ["Tacos", "Beans"] },
        Sunday: { Morning: ["Waffles", "Juice"], Afternoon: ["Roast Chicken", "Potatoes"], Night: ["Pasta", "Salad"] }
    };

    // Meal costs
    const mealCosts = {
        "Pancakes": 300, "Omelette": 200, "Rice & Curry": 500, "Salad": 200,
        "Pizza": 600, "Soup": 300, "Cereal": 200, "Fruits": 200,
        "Pasta": 400, "Garlic Bread": 300, "Grilled Chicken": 700, "Veggies": 300,
        "French Toast": 300, "Milk": 100, "Biryani": 600, "Raita": 200,
        "Burger": 500, "Fries": 300, "Poha": 200, "Tea": 100,
        "Chapati & Dal": 400, "Fish Curry": 700, "Rice": 300, "Smoothie": 300,
        "Sandwich": 400, "Noodles": 500, "Spring Rolls": 400, "BBQ": 800,
        "Mashed Potatoes": 300, "Idli": 200, "Sambhar": 300, "Pulao": 600,
        "Curd": 200, "Tacos": 500, "Beans": 300, "Waffles": 400, "Juice": 200,
        "Roast Chicken": 700, "Potatoes": 300
    };

    function getCurrentMeal() {
        const hours = new Date().getHours();
        if (hours < 12) return "Morning";
        if (hours < 18) return "Afternoon";
        return "Night";
    }

    function loadCurrentMenu() {
        const day = new Date().toLocaleDateString('en-US', { weekday: 'long' });
        const mealTime = getCurrentMeal();
        const menuList = document.getElementById("menu-list");
        const mealTimeHeader = document.getElementById("meal-time");
        const totalCostDisplay = document.getElementById("total-cost");

        mealTimeHeader.textContent = `${day} - ${mealTime}`;
        menuList.innerHTML = "";

        totalCost = 0;
        current_menu_list = {};  // Reset menu list
        current_menu_list_totalCost = 0;  // Reset cost

        let currentStudentID = localStorage.getItem("currentStudentID");

        if (!currentStudentID) {
            document.getElementById("student-input-modal").classList.remove("hidden");
            document.getElementById("current-menu-container").classList.add("hidden");
            return;
        }

        // Get previous selections for the student
        let studentMenu = JSON.parse(localStorage.getItem(`menu_${currentStudentID}`)) || {};

        menuData[day][mealTime].forEach(item => {
            const li = document.createElement("li");
            li.className = "flex items-center space-x-2";

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.className = "mr-2";
            checkbox.checked = studentMenu[item] === true; // Keep previous selections

            const itemCost = mealCosts[item] || 0;
            const itemLabel = document.createTextNode(`${item} ($${itemCost})`);

            li.appendChild(checkbox);
            li.appendChild(itemLabel);
            menuList.appendChild(li);

            // Store item in current menu list regardless of selection
            current_menu_list[item] = true;  // true if checked, false if not
            current_menu_list_totalCost += itemCost;

            // Update selection on change
            checkbox.addEventListener("change", () => {
                studentMenu[item] = checkbox.checked;
                // current_menu_list[item] = checkbox.checked;


                localStorage.setItem(`menu_${currentStudentID}`, JSON.stringify(studentMenu));
                // localStorage.setItem("currentMenu", JSON.stringify(current_menu_list));
                // localStorage.setItem("currentMenuTotalCost", current_menu_list_totalCost);
                calculateTotalCost(studentMenu);
            });
        });

        // Save the full menu to localStorage
        localStorage.setItem("currentMenu", JSON.stringify(current_menu_list));
        localStorage.setItem("currentMenuTotalCost", current_menu_list_totalCost);

        calculateTotalCost(studentMenu);
    }


    function calculateTotalCost(studentMenu) {
        totalCost = 0;
        current_menu_list_totalCost = 0;

        Object.keys(studentMenu).forEach(item => {
            if (studentMenu[item]) {
                totalCost += mealCosts[item] || 0;
                current_menu_list_totalCost += mealCosts[item] || 0;
            }
        });

        document.getElementById("total-cost").textContent = `Total Cost: $${totalCost}`;
        localStorage.setItem("totalCost", totalCost);
        // localStorage.setItem("currentMenuTotalCost", current_menu_list_totalCost);
    }




    function showWeeklyMenu() {
        const weeklyMenu = document.getElementById("weekly-menu");
        weeklyMenu.classList.toggle("hidden");
        const weeklyMenuBody = document.getElementById("weekly-menu-body");
        weeklyMenuBody.innerHTML = "";

        Object.keys(menuData).forEach(day => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td class="border border-gray-300 p-2">${day}</td>
                <td class="border border-gray-300 p-2">${menuData[day].Morning.join(", ")}</td>
                <td class="border border-gray-300 p-2">${menuData[day].Afternoon.join(", ")}</td>
                <td class="border border-gray-300 p-2">${menuData[day].Night.join(", ")}</td>
            `;
            weeklyMenuBody.appendChild(row);
        });
    }

    loadCurrentMenu();
    window.showWeeklyMenu = showWeeklyMenu;
});
