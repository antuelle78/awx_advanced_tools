#!/bin/bash
# Simple Testing Menu for Multi-Server MCP

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║        Multi-Server MCP - Testing Menu                   ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Choose a test to run:"
echo ""
echo "  1) Quick Status Check (health + AWX)"
echo "  2) List All Resources (templates, inventories, hosts)"
echo "  3) Test Specific Server"
echo "  4) Open API Documentation (browser)"
echo "  5) View Server Logs"
echo "  6) Performance Test"
echo "  7) Run Full Test Suite"
echo "  0) Exit"
echo ""
read -p "Enter choice [0-7]: " choice

case $choice in
    1)
        echo ""
        echo "=== QUICK STATUS CHECK ==="
        echo ""
        echo "Health Checks:"
        curl -s http://localhost:8001/health | jq -c
        curl -s http://localhost:8002/health | jq -c
        curl -s http://localhost:8003/health | jq -c
        echo ""
        echo "AWX Connectivity:"
        curl -s http://localhost:8001/test | jq -c
        curl -s http://localhost:8002/test | jq -c
        curl -s http://localhost:8003/test | jq -c
        echo ""
        ;;
    2)
        echo ""
        echo "=== ALL RESOURCES ==="
        echo ""
        echo "Job Templates:"
        curl -s http://localhost:8001/job_templates | jq '.results[] | {id, name}'
        echo ""
        echo "Inventories:"
        curl -s http://localhost:8002/inventories | jq '.results[] | {id, name}'
        echo ""
        echo "Hosts (first 10):"
        curl -s http://localhost:8002/hosts | jq '.results[0:10] | .[] | {id, name, inventory}'
        echo ""
        ;;
    3)
        echo ""
        echo "Which server?"
        echo "  1) Core Operations (8001)"
        echo "  2) Inventory Management (8002)"
        echo "  3) Templates (8003)"
        read -p "Enter choice: " server
        case $server in
            1) 
                echo ""
                curl -s http://localhost:8001/ | jq
                ;;
            2)
                echo ""
                curl -s http://localhost:8002/ | jq
                ;;
            3)
                echo ""
                curl -s http://localhost:8003/ | jq
                ;;
        esac
        ;;
    4)
        echo ""
        echo "Opening API documentation in browser..."
        echo ""
        echo "Core Operations:        http://localhost:8001/docs"
        echo "Inventory Management:   http://localhost:8002/docs"
        echo "Templates:              http://localhost:8003/docs"
        echo ""
        xdg-open http://localhost:8001/docs 2>/dev/null || open http://localhost:8001/docs 2>/dev/null || echo "Please open manually"
        ;;
    5)
        echo ""
        echo "Which server logs?"
        echo "  1) Core Operations"
        echo "  2) Inventory Management"
        echo "  3) Templates"
        echo "  4) All servers"
        read -p "Enter choice: " logs
        cd /home/ghost/awx_advanced_tools/mcp-server
        case $logs in
            1) docker compose -f docker-compose.multi.yml logs --tail=50 core ;;
            2) docker compose -f docker-compose.multi.yml logs --tail=50 inventory ;;
            3) docker compose -f docker-compose.multi.yml logs --tail=50 templates ;;
            4) docker compose -f docker-compose.multi.yml logs --tail=50 ;;
        esac
        ;;
    6)
        echo ""
        echo "=== PERFORMANCE TEST ==="
        for port in 8001 8002 8003; do
            echo ""
            echo "Testing port $port..."
            START=$(date +%s%N)
            curl -s http://localhost:$port/health > /dev/null
            END=$(date +%s%N)
            DURATION=$(( (END - START) / 1000000 ))
            echo "Response time: ${DURATION}ms"
        done
        echo ""
        ;;
    7)
        echo ""
        ./run_tests.sh
        ;;
    0)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
