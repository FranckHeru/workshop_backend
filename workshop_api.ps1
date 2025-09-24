# workshop_api.ps1
$ApiBase = "http://127.0.0.1:8000/api"
$User = "admin"
$Pass =  [Environment]::GetEnvironmentVariable("WORKSHOP_SQL_SA_PWD","Machine")

function Get-JwtToken {
    param(
        [string]$Username,
        [string]$Password
    )
    $url = "$ApiBase/auth/jwt/create/"
    $body = @{ username = $Username; password = $Password } | ConvertTo-Json
    $res = Invoke-RestMethod -Method POST -Uri $url -ContentType "application/json" -Body $body
    return $res.access
}

function Invoke-Api {
    param(
        [ValidateSet("GET","POST","PUT","PATCH","DELETE")]
        [string]$Method,
        [string]$Path,
        $BodyObject
    )
    if (-not $script:Token) {
        $script:Token = Get-JwtToken -Username $User -Password $Pass
        Write-Host "ðŸ”‘ Access token obtenido."
    }
    $headers = @{ Authorization = "Bearer $script:Token" }
    if ($BodyObject) {
        $json = $BodyObject | ConvertTo-Json -Depth 6
        return Invoke-RestMethod -Method $Method -Uri "$ApiBase/$Path" -Headers $headers -ContentType "application/json" -Body $json
    } else {
        return Invoke-RestMethod -Method $Method -Uri "$ApiBase/$Path" -Headers $headers
    }
}

Write-Host "== Workshop API quick smoke =="

# 1) Listado (deberÃ­a responder 200)
$customers = Invoke-Api -Method GET -Path "customers/"
$customers | Format-Table -AutoSize

# 2) Crear cliente
$newCustomer = Invoke-Api -Method POST -Path "customers/" -BodyObject @{
    type = "PERSON"
    name = "Cliente PS1"
    email = "ps1@example.com"
    phone = "7777-8888"
    address = "Calle PowerShell"
    is_active = $true
}
Write-Host "ðŸ†• Customer ID:" $newCustomer.id

# 3) Crear vehÃ­culo (nota: usa el id del cliente reciÃ©n creado)
$newVehicle = Invoke-Api -Method POST -Path "vehicles/" -BodyObject @{
    plate = "P123-456"
    brand = "Toyota"
    model = "Corolla"
    year = 2018
    mileage_km = 85000
    owner = $newCustomer.id
}
Write-Host "ðŸš— Vehicle ID:" $newVehicle.id

# 4) Crear servicio y repuesto (opcional)
$service = Invoke-Api -Method POST -Path "services/" -BodyObject @{
    code = "REV-GEN"
    name = "RevisiÃ³n general"
    description = "Chequeo bÃ¡sico"
    labor_minutes = 60
    price = "25.00"
    is_active = $true
}
Write-Host "ðŸ› ï¸ Service ID:" $service.id

$part = Invoke-Api -Method POST -Path "parts/" -BodyObject @{
    sku = "FILT-ACEITE-001"
    name = "Filtro de aceite"
    unit = "UNI"
    stock = "5.00"
    cost = "3.00"
    price = "6.50"
    is_active = $true
}
Write-Host "ðŸ”© Part ID:" $part.id

# 5) Crear orden de trabajo (opcional)
$wo = Invoke-Api -Method POST -Path "workorders/" -BodyObject @{
    number = "WO-0001"
    status = "OPEN"
    complaint = "Ruidos en suspensiÃ³n"
    customer = $newCustomer.id
    vehicle = $newVehicle.id
}
Write-Host "ðŸ“„ WorkOrder ID:" $wo.id

Write-Host "âœ… Listo. Pruebas bÃ¡sicas OK."

