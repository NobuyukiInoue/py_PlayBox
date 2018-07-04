param( $musicFile, $timbre )

##--------------------------------------------------------##
## ���K��`�t�@�C���̓ǂݍ���
##--------------------------------------------------------##
function loadDefFile([string]$defFileName)
{
    $f = (Get-Content $defFileName) -as [string[]]
    $lines = @()

    # ���K���ƃm�[�g�i���o�[�ɕ����A�z��Ɋi�[����
    foreach ($currentLine in $f) {

        # �R�����g�J�n�ʒu�̌��o
        $commentStartPostion = $currentLine.IndexOf("//")

        if ($commentStartPostion -eq 0) {
            continue
        }
        elseif ($commentStartPostion -gt 0) {
            $currentLine = $currentLine.Substring(0, $commentStartPostion)
        }

        # �X�y�[�X�̍폜
        $currentLine = $currentLine.Replace(" ","")

        # TAB�̍폜
        $currentLine = $currentLine.Replace("`t", "")

        # "="�ŋ�؂�A���K�ƃm�[�g�i���o�[�ɕ����Ċi�[����
        if ($currentLine -ne "") {
            $scale, $note = $currentLine -split "="
            $lines += New-Object PSObject -Property @{scale=$scale; note=$note}
        }
    }
    
    return($lines)
}

##--------------------------------------------------------##
## �����t�@�C���̓ǂݍ���
##--------------------------------------------------------##
function loadPlayFile([string]$musicFile)
{
    $f = (Get-Content $musicFile) -as [string[]]
    $lines = @()

    foreach ($currentLine in $f) {

        # �R�����g�J�n�ʒu�̌��o
        $commentStartPostion = $currentLine.IndexOf("//")

        if ($commentStartPostion -eq 0) {
            continue
        }
        elseif ($commentStartPostion -gt 0) {
            $currentLine = $currentLine.Substring(0, $commentStartPostion)
        }

        # �X�y�[�X�̍폜
        $currentLine = $currentLine.Replace(" ","")

        # TAB�̍폜
        $currentLine = $currentLine.Replace("`t", "")

        # "="�ŋ�؂�A���K�ƒ�����z��Ɋi�[����
        if ($currentLine -ne "") {
            $scale, $tlen = $currentLine -split "="
            $lines += New-Object PSObject -Property @{scale=$scale; note=""; tlen=$tlen}
        }
    }

    return($lines)
}

##--------------------------------------------------------##
## ���K��������������A�m�[�g�i���o�[���Z�b�g����
##--------------------------------------------------------##
function replaceScalt_to_Freq([array]$defs, [array]$playData)
{
    for ($i = 0; $i -lt $playData.Length; $i++) {

        $scale = $playData[$i].scale -split ","

        foreach ($temp in $scale) {

            for ($j = 0; $j -lt $defs.Length; $j++) {

                if ($temp -eq $defs[$j].scale) {

                    if ($playData[$i].note -eq "") {
                       $playData[$i].note = $defs[$j].note
                    }
                    else {
                       $playData[$i].note += "," + $defs[$j].note
                    }

                    break
                }
            }
        }
    }
    
    return($playData)
}

<#
##--------------------------------------------------------##
## 16�i��������𐔒l�ɕϊ�����
##--------------------------------------------------------##
function toHex([string]tempStr)
{
	$ret = [Convert]::ToInt32($tempStr, 16)
	return($ret)
}
#>

##--------------------------------------------------------##
## Main
##--------------------------------------------------------##

if (-Not($musicFile)) {
    Write-Host "Usage : PlayMIDI.ps1 musicDataFile <timbre>"
    exit
}

if (-Not($timbre)) {
    $timbre = 1     # �s�A�m
}

$defs = @()
$defs = loadDefFile "note-number.dat" 

$playData = @()
$playData = loadPlayFile $musicFile

# ���K��MIDI�m�[�g�i���o�[�ɕϊ�����
$playData = replaceScalt_to_Freq $defs $playData


##-----------------------------------------##
## CSharp���C�u�����̓ǂݍ���(Win32API�Q��)
##-----------------------------------------##
add-type -path .\myMIDI.cs -passThru
$pm = New-Object myMIDI

$initData = [UINT32]$timbre*256 + [Convert]::ToInt32("c0", 16)
$pm.INIT($initData)    # MIDI������

Write-Host
Write-Host "Load Done. Play Start!!"

for ($i = 0; $i -lt $playData.Length; $i++) {

    if ($playData[$i].note -ne "") {
        Write-Host "[$i] = "$playData[$i].scale"("$playData[$i].note"), "$playData[$i].tlen"[ms]"

        $cnote = $playData[$i].note -split ","

        foreach ($data in $cnote) {

            # MIDI�ɏo�͂���
            $note_on = "7f" + $data + "90"
            $play_on = [Convert]::ToInt32($note_on, 16)

            # ���Ղ�����
            $pm.OutOnly($play_on)
        }

        # ��莞�Ԗ炵������
        $pm.Sleep($playData[$i].tlen)

        foreach ($data in $cnote) {
            $note_off = "7f" + $data + "80"
            $play_off = [Convert]::ToInt32($note_off, 16)

            # ���Ղ𗣂�
            $pm.OutOnly($play_off)
        }
    } 
    else {
        Write-Host "[$i] = rest ("$playData[$i].note"), "$playData[$i].tlen"[ms]"

        # �x��
        $pm.Sleep($playData[$i].tlen)
    }
}

$pm.Close()
