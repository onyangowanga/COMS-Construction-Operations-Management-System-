# Demo Data Setup for Client Pitches

This guide explains how to populate your COMS database with realistic demo data for client presentations.

## Overview

The seed data command creates:
- **5 Construction Projects** (various types and stages)
- **5 Suppliers** (building materials, cement, steel, electrical, timber)
- **5 Subcontractors** (electrical, plumbing, steel, finishes, groundworks)
- **Multiple LPOs** (Local Purchase Orders)
- **Multiple Subcontracts** with claims
- **Client Payments** for active projects
- **Project Stages** for implementation tracking

## Quick Start

### 1. Access the Backend Container

The seed command must be run inside the Docker container where Django and dependencies are installed.

```bash
# SSH into your VPS
ssh root@156.232.88.156

# Navigate to project directory
cd /root/coms

# Access the Django web service (docker-compose service name is 'web', not 'backend')
docker-compose -f docker-compose.prod.yml exec web bash
```

### 2. Run the Seed Command

```bash
# Seed demo data
python manage.py seed_demo_data

# Or clear existing data first, then seed
python manage.py seed_demo_data --clear
```

**Important**: Run this command INSIDE the Docker container. Do NOT run it from the host machine.

If you get `ModuleNotFoundError: No module named 'django'`, you are running on the host machine instead of inside the container.

## What Gets Created

### Projects (5)

1. **Riverside Corporate Towers** (PRJ-2026-001)
   - Type: New Construction
   - Value: KES 450,000,000
   - Status: Implementation
   - Location: Westlands, Nairobi
   - Client: Riverside Development Corporation

2. **Green Valley Residential Estate** (PRJ-2026-002)
   - Type: New Construction
   - Value: KES 280,000,000
   - Status: Implementation
   - Location: Karen, Nairobi
   - Client: Green Valley Developers

3. **City Mall Renovation** (PRJ-2026-003)
   - Type: Renovation
   - Value: KES 85,000,000
   - Status: Implementation
   - Location: CBD, Nairobi
   - Client: Metro Retail Properties

4. **Industrial Park Warehouse Complex** (PRJ-2025-015)
   - Type: New Construction
   - Value: KES 320,000,000
   - Status: **Completed** ✅
   - Location: Athi River
   - Client: Logistics Hub Africa

5. **University Science Complex** (PRJ-2026-004)
   - Type: New Construction
   - Value: KES 550,000,000
   - Status: Approval
   - Location: Kikuyu, Kiambu
   - Client: National University of Kenya

### Suppliers (5)

1. **BuildMart Suppliers Ltd**
   - Phone: +254722123456
   - Tax PIN: P051234567A
   - Location: Industrial Area

2. **Kenya Cement Distributors**
   - Phone: +254733234567
   - Tax PIN: P051234568B
   - Location: Mombasa Road

3. **Prime Steel & Hardware**
   - Phone: +254711345678
   - Tax PIN: P051234569C
   - Location: Ruaraka

4. **ElectroPro Solutions**
   - Phone: +254720456789
   - Tax PIN: P051234570D
   - Location: Westlands

5. **Timber & Finishes Co.**
   - Phone: +254734567890
   - Tax PIN: P051234571E
   - Location: Thika Road

### Subcontractors (5)

1. **Excel Electrical Contractors**
   - Specialization: Electrical Works
   - Contact: John Kamau
   - Tax Number: P051234580A

2. **Premium Plumbing Services**
   - Specialization: Plumbing & Drainage
   - Contact: Mary Wanjiku
   - Tax Number: P051234581B

3. **Skyline Steel Fabricators**
   - Specialization: Steel Fabrication & Erection
   - Contact: David Omondi
   - Tax Number: P051234582C

4. **Interior Finishing Experts**
   - Specialization: Interior Finishes & Joinery
   - Contact: Sarah Njeri
   - Tax Number: P051234583D

5. **Foundation & Ground Works Ltd**
   - Specialization: Earthworks & Foundation
   - Contact: Peter Mwangi
   - Tax Number: P051234584E

### Additional Data

- **Local Purchase Orders (LPOs)**: 6-12 LPOs across active projects
- **Subcontract Agreements**: 4-6 subcontracts with varying stages
- **Subcontract Claims**: Multiple payment claims per subcontract
- **Client Payments**: Progress payments for active projects
- **Project Stages**: 4 stages per project (Preliminary, Shell, Finishes, External Works)

## Organization Created

**Organization**: Premier Construction Ltd
- Currency: KES
- Fiscal Year: January 1

## Verification

After seeding, you can verify the data through:

1. **Django Admin Panel**:
   ```
   http://156.232.88.156:8000/admin/
   ```

2. **API Endpoints**:
   ```bash
   # Projects
   curl http://156.232.88.156:8000/api/projects/

   # Suppliers
   curl http://156.232.88.156:8000/api/suppliers/

   # Subcontractors
   curl http://156.232.88.156:8000/api/subcontractors/
   ```

3. **Frontend Dashboard**:
   ```
   http://156.232.88.156:3000/dashboard
   ```

## Customization

To modify the seed data, edit:
```
COMS/apps/core/management/commands/seed_demo_data.py
```

You can customize:
- Project names, values, and locations
- Supplier/subcontractor details
- LPO amounts and statuses
- Contract values and terms
- Payment schedules

## Clearing Data

To remove all demo data before re-seeding:

```bash
python manage.py seed_demo_data --clear
```

**Warning**: This will delete all projects, suppliers, and subcontractors for the DEMO organization.

## Troubleshooting

### Command not found

Make sure you're inside the Docker container:
```bash
docker-compose -f docker-compose.prod.yml exec web bash
```

### Organization already exists

The command will reuse the existing "DEMO" organization. To start fresh:
```bash
python manage.py seed_demo_data --clear
```

### Permission errors

Ensure migrations are up to date:
```bash
python manage.py migrate
```

## For Client Presentations

When demoing to clients, highlight:

✅ **Multiple Active Projects**: Show variety in project types and stages
✅ **Financial Tracking**: Demonstrate LPOs, subcontracts, and payment claims
✅ **Supplier Management**: Show comprehensive supplier database
✅ **Subcontractor Workflow**: Display contract management and claims processing
✅ **Real-world Scale**: Projects ranging from KES 85M to KES 550M
✅ **Completion Tracking**: Show completed projects alongside active ones

## Next Steps

1. Create test users with different roles
2. Generate sample reports using the demo data
3. Test workflow approvals with the demo projects
4. Export sample financial reports for presentation

---

**Need help?** Check the main README or contact the development team.
