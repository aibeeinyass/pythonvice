import streamlit as st
import random
import time
import json
import os

# --- CONSTANTS ---
DISTRICTS = {
    "Downtown": {"risk": 0.1, "multiplier": 1.0, "desc": "Safe but low profit."},
    "The Docks": {"risk": 0.4, "multiplier": 2.5, "desc": "Heavy smuggling area."},
    "Vinewood": {"risk": 0.2, "multiplier": 1.5, "desc": "High-end luxury area."},
    "Industrial": {"risk": 0.6, "multiplier": 4.0, "desc": "High risk, high reward."}
}

CARS = {
    "Rusty Banger": {"price": 0, "protection": 0, "img": "🚗"},
    "Speedster": {"price": 5000, "protection": 1, "img": "🏎️"},
    "Armored Truck": {"price": 25000, "protection": 3, "img": "🚛"},
    "Ghost Rider": {"price": 100000, "protection": 5, "img": "🏍️"}
}

WEAPONS = {
    "Brass Knuckles": {"price": 500, "power": 10},
    "Uzi": {"price": 5000, "power": 30},
    "RPG": {"price": 50000, "power": 80}
}

MARKET_ITEMS = ["Crypto", "Luxury Watches", "Gold Bars", "Art"]

# --- GAME ENGINE ---
def init_state():
    if 'gs' not in st.session_state:
        if os.path.exists("savegame.json"):
            with open("savegame.json", "r") as f:
                st.session_state.gs = json.load(f)
        else:
            st.session_state.gs = {
                "cash": 2000, "heat": 0, "xp": 0, "level": 1,
                "hp": 100, "location": "Downtown", "car": "Rusty Banger",
                "weapon": "None", "inventory": {i: 0 for i in MARKET_ITEMS},
                "logs": ["Welcome to Python Vice. Start a heist or trade goods."]
            }
        # Dynamic market prices
        st.session_state.prices = {i: random.randint(100, 500) for i in MARKET_ITEMS}

def save_game():
    with open("savegame.json", "w") as f:
        json.dump(st.session_state.gs, f)

def add_log(msg):
    st.session_state.gs["logs"].insert(0, f"[{time.strftime('%H:%M')}] {msg}")
    if len(st.session_state.gs["logs"]) > 10:
        st.session_state.gs["logs"].pop()

# --- ACTION FUNCTIONS ---
def handle_travel(loc):
    gs = st.session_state.gs
    gs["location"] = loc
    # Update prices based on district
    for item in MARKET_ITEMS:
        st.session_state.prices[item] = int(random.randint(100, 1000) * DISTRICTS[loc]["multiplier"])
    
    # Random Events
    event = random.random()
    if event < 0.15: # Combat
        enemy_power = random.randint(10, 40)
        player_power = WEAPONS.get(gs["weapon"], {"power": 5})["power"]
        if player_power >= enemy_power:
            win_loot = random.randint(500, 1500)
            gs["cash"] += win_loot
            add_log(f"💥 Ambushed in {loc}! You fought them off and looted ${win_loot}.")
        else:
            gs["hp"] -= 30
            add_log(f"🤕 Ambushed! You took 30 damage escaping.")
    
    elif event < DISTRICTS[loc]["risk"]:
        gs["heat"] += 1
        add_log(f"🚨 Police are watching you in {loc}!")

    if gs["hp"] <= 0:
        gs["hp"] = 100
        gs["cash"] = int(gs["cash"] * 0.5)
        add_log("💀 WASTED. You woke up in the hospital. 50% cash lost.")

def start_heist():
    gs = st.session_state.gs
    with st.spinner("Hacking security..."):
        time.sleep(1.5)
        success_rate = 0.6 + (CARS[gs["car"]]["protection"] * 0.05)
        if random.random() < success_rate:
            loot = random.randint(2000, 5000) * gs["level"]
            gs["cash"] += loot
            gs["xp"] += 50
            gs["heat"] += 1
            add_log(f"💰 SUCCESS! You cleaned out the vault for ${loot}.")
            if gs["xp"] >= gs["level"] * 100:
                gs["level"] += 1
                gs["xp"] = 0
                add_log("⭐ LEVEL UP! You are now more influential.")
        else:
            gs["heat"] += 2
            gs["hp"] -= 20
            add_log("👮 HEIST FAILED! You barely escaped the SWAT team.")

# --- UI LAYOUT ---
st.set_page_config(page_title="Python Vice: Streamlit Edition", layout="wide")
init_state()
gs = st.session_state.gs

# Sidebar Stats
with st.sidebar:
    st.title("🕶️ Python Vice")
    st.metric("Cash", f"${gs['cash']:,}", delta=None)
    st.metric("Level", gs['level'])
    st.progress(gs['hp']/100, text=f"HP: {gs['hp']}%")
    st.progress(gs['heat']/5, text=f"Heat: {gs['heat']}/5")
    
    if st.button("🧼 Bribe Cops ($2,000)") and gs["cash"] >= 2000:
        gs["cash"] -= 2000
        gs["heat"] = 0
        st.rerun()
    
    if st.button("💾 Save Game"):
        save_game()
        st.success("Game Saved!")

# Main Dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📍 Location: {gs['location']}")
    
    # Map/Travel Tabs
    tab_map, tab_market, tab_garage, tab_armory = st.tabs(["🗺️ Map", "💹 Market", "🏎️ Garage", "🔫 Armory"])
    
    with tab_map:
        st.write("Travel to a new district to change market prices.")
        cols = st.columns(len(DISTRICTS))
        for i, (name, info) in enumerate(DISTRICTS.items()):
            with cols[i]:
                if st.button(f"Go to {name}"):
                    handle_travel(name)
                    st.rerun()
                st.caption(info["desc"])
        
        st.divider()
        st.subheader("Current Mission")
        if st.button("🏦 EXECUTE BANK HEIST", use_container_width=True, type="primary"):
            start_heist()
            st.rerun()

    with tab_market:
        st.write("Buy low, sell high.")
        for item in MARKET_ITEMS:
            p = st.session_state.prices[item]
            inv = gs["inventory"][item]
            m_col1, m_col2, m_col3 = st.columns([2, 1, 1])
            m_col1.write(f"**{item}** \nPrice: ${p:,}")
            if m_col2.button(f"Buy {item}", key=f"b_{item}"):
                if gs["cash"] >= p:
                    gs["cash"] -= p
                    gs["inventory"][item] += 1
                    add_log(f"Purchased {item}")
                    st.rerun()
            if m_col3.button(f"Sell {item}", key=f"s_{item}"):
                if inv > 0:
                    gs["cash"] += p
                    gs["inventory"][item] -= 1
                    add_log(f"Sold {item}")
                    st.rerun()

    with tab_garage:
        for name, data in CARS.items():
            g_col1, g_col2 = st.columns([3, 1])
            status = "(Owned)" if gs["car"] == name else f"${data['price']:,}"
            g_col1.write(f"{data['img']} **{name}** \nBuff: -{data['protection']} Heat Risk")
            if gs["car"] != name:
                if g_col2.button(f"Buy for {status}", key=f"car_{name}"):
                    if gs["cash"] >= data["price"]:
                        gs["cash"] -= data["price"]
                        gs["car"] = name
                        st.rerun()

    with tab_armory:
        for name, data in WEAPONS.items():
            a_col1, a_col2 = st.columns([3, 1])
            status = "(Equipped)" if gs["weapon"] == name else f"${data['price']:,}"
            a_col1.write(f"⚔️ **{name}** \nPower: {data['power']}")
            if gs["weapon"] != name:
                if a_col2.button(f"Buy {status}", key=f"wep_{name}"):
                    if gs["cash"] >= data["price"]:
                        gs["cash"] -= data["price"]
                        gs["weapon"] = name
                        st.rerun()

with col2:
    st.subheader("📰 Log Feed")
    for log in gs["logs"]:
        st.caption(log)
    
    st.divider()
    st.subheader("🎰 Diamond Casino")
    st.write("Bet $500 on the slots!")
    if st.button("🎰 SPIN"):
        if gs["cash"] >= 500:
            gs["cash"] -= 500
            res = [random.choice(["🍒", "💎", "7️⃣", "🍀"]) for _ in range(3)]
            st.header(f"{res[0]} | {res[1]} | {res[2]}")
            if len(set(res)) == 1:
                gs["cash"] += 10000
                st.balloons()
                add_log("🎰 JACKPOT! You won $10,000!")
            elif len(set(res)) == 2:
                gs["cash"] += 1000
                st.success("Small Win! +$1,000")
            else:
                st.error("You lost.")
            st.rerun()