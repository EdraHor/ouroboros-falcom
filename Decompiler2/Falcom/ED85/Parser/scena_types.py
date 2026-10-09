from Falcom.ED84.Parser.scena_types import *
from Falcom.ED84.Parser import scena_types as ed84

ScenaAlgoTableEntry.InvalidID = 0xFFFF
ScenaBreakTable.InvalidID = 0xFFFF

class ScenaBattleSetting:
    def __init__(
        self,
        mapName     : str = '',
        x           : int = 0,
        y           : int = 0,
        z           : int = 0,
        direction   : int = 0,
        length      : int = 0,
        width       : int = 0,
        battleId    : int = 0,
        flags       : int = 0,
        bgm         : int = 0,
        dangerBGM   : int = 0,
        word34      : int = 0,
        word36      : int = 0,
        atBonus     : int = 0,
        battleScript: str = '',
        monsterSet  : List[ScenaBattleMonsterSet] = None,
        *,
        fs: fileio.FileStream = None,
    ):

        self.mapName        = mapName       # type: str
        self.x              = x             # type: int
        self.y              = y             # type: int
        self.z              = z             # type: int
        self.direction      = direction     # type: int
        self.length         = length        # type: int
        self.width          = width         # type: int
        self.battleId       = battleId      # type: int
        self.flags          = flags         # type: int
        self.bgm            = bgm           # type: int
        self.dangerBGM      = dangerBGM     # type: int
        self.word34         = word34        # type: int
        self.word36         = word36        # type: int
        self.atBonus        = atBonus       # type: int
        self.battleScript   = battleScript  # type: str
        self.monsterSet     = monsterSet    # type: List[ScenaBattleMonsterSet]

        self.read(fs)

    def read(self, fs: fileio.FileStream):
        if not fs:
            return

        self.mapName    = utils.read_fixed_string(fs, 0x10)     # 0x00
        self.x          = fs.ReadFloat()                        # 0x10
        self.y          = fs.ReadFloat()                        # 0x14
        self.z          = fs.ReadFloat()                        # 0x18
        self.direction  = fs.ReadFloat()                        # 0x1C
        self.length     = fs.ReadFloat()                        # 0x20
        self.width      = fs.ReadFloat()                        # 0x24
        self.battleId   = fs.ReadUShort()                       # 0x28

        fs.Position += 2    # padding                           # 0x2A

        self.flags          = fs.ReadULong()                        # 0x2C
        self.bgm            = fs.ReadUShort()                       # 0x30
        self.dangerBGM      = fs.ReadUShort()                       # 0x32
        self.word34         = fs.ReadUShort()                       # 0x34
        self.word36         = fs.ReadUShort()                       # 0x36
        self.atBonus        = fs.ReadULong()                        # 0x38
        self.battleScript   = utils.read_fixed_string(fs, 0x20)     # 0x3C

        self.monsterSet = []                                    # 0x4C

        for _ in range(255):
            monset = ScenaBattleMonsterSet(fs = fs)
            if monset.id == ScenaBattleMonsterSet.InvalidID:
                break

            self.monsterSet.append(monset)

    def serialize(self) -> bytes:
        fs = io.BytesIO()

        fs.write(utils.pad_string(self.mapName, 0x10))
        fs.write(utils.float_to_bytes(self.x))
        fs.write(utils.float_to_bytes(self.y))
        fs.write(utils.float_to_bytes(self.z))
        fs.write(utils.float_to_bytes(self.direction))
        fs.write(utils.float_to_bytes(self.length))
        fs.write(utils.float_to_bytes(self.width))
        fs.write(utils.int_to_bytes(self.battleId, 2))

        fs.write(b'\x00' * 2) # padding

        fs.write(utils.int_to_bytes(self.flags, 4))
        fs.write(utils.int_to_bytes(self.bgm, 2))
        fs.write(utils.int_to_bytes(self.dangerBGM, 2))
        fs.write(utils.int_to_bytes(self.word34, 2))
        fs.write(utils.int_to_bytes(self.word36, 2))
        fs.write(utils.int_to_bytes(self.atBonus, 4))
        fs.write(utils.pad_string(self.battleScript, 0x20))

        for monset in self.monsterSet:
            fs.write(monset.serialize())

        if not self.monsterSet or self.monsterSet[-1].id != ScenaBattleMonsterSet.InvalidID:
            fs.write(ScenaBattleMonsterSet(ScenaBattleMonsterSet.InvalidID).serialize())

        return fs.getvalue()

    def toPython(self) -> List[str]:
        body = [
            f'ScenaBattleSetting(',
            f'{DefaultIndent}mapName        = \'{self.mapName}\',',
            f'{DefaultIndent}x              = {self.x},',
            f'{DefaultIndent}y              = {self.y},',
            f'{DefaultIndent}z              = {self.z},',
            f'{DefaultIndent}direction      = {self.direction},',
            f'{DefaultIndent}length         = {self.length},',
            f'{DefaultIndent}width          = {self.width},',
            f'{DefaultIndent}battleId       = {self.battleId},',
            f'{DefaultIndent}flags          = 0x{self.flags:08X},',
            f'{DefaultIndent}bgm            = {self.bgm},',
            f'{DefaultIndent}dangerBGM      = {self.dangerBGM},',
            f'{DefaultIndent}word34         = {self.word34},',
            f'{DefaultIndent}word36         = {self.word36},',
            f'{DefaultIndent}atBonus        = {self.atBonus},',
            f'{DefaultIndent}battleScript   = \'{self.battleScript}\',',
            f'{DefaultIndent}monsterSet     = [',
        ]

        indent2 = DefaultIndent * 2
        for monset in self.monsterSet:
            body.extend([indent2 + l for l in monset.toPython()])
            body[-1] += ','

        body.append(f'{DefaultIndent}],')
        body.append(f')')

        return body

class ScenaActionTableEntry(ed84.ScenaActionTableEntry):
    def hasExitCode(self):
        return True

class ScenaAlgoTableEntry(ed84.ScenaAlgoTableEntry):
    def hasExitCode(self):
        return True

class ScenaActionTable(ed84.ScenaActionTable):
    def serialize(self) -> bytes:
        b = bytearray()
        for e in self.actions:
            b.extend(e.serialize())

        if not self.actions or self.actions[-1].craftId != ScenaActionTableEntry.InvalidCraftID:
            b.extend(ScenaActionTableEntry(craftId = ScenaActionTableEntry.InvalidCraftID).serialize())

        return bytes(b)

    def read(self, fs: fileio.FileStream):
        # the same loop as in ED83, but with the Reverie entries (the terminator is a full entry, see hasExitCode)
        if not fs:
            return

        self.actions = []
        for _ in range(0x40):
            entry = ScenaActionTableEntry(fs = fs)
            if entry.craftId == ScenaActionTableEntry.InvalidCraftID:
                break

            self.actions.append(entry)

class ScenaAlgoTable(ed84.ScenaAlgoTable):
    def read(self, fs: fileio.FileStream):
        # the same loop as in ED83, but with the Reverie entries (the terminator is a full entry, see hasExitCode)
        if not fs:
            return

        self.entries = []
        for _ in range(0x40):
            if fs.Remaining < 0x20:     # no room for another entry: no terminator (almon355_c01)
                self._noTerm = True
                break

            e = ScenaAlgoTableEntry(fs = fs)

            self.entries.append(e)
            if e.craftId == ScenaAlgoTableEntry.InvalidID:
                break

class ScenaReactionTable(ed84.ScenaReactionTable):
    # Reverie ends the table with a 0xFFFF entry (kept as an entry); without it 8 entries fill the table
    EndID = 0xFFFF

    def read(self, fs: fileio.FileStream):
        if not fs:
            return

        self.reactions = []
        for _ in range(8):
            e = ScenaReactionTableEntry(fs = fs)
            if e.craftId == ScenaReactionTableEntry.InvalidID:
                break

            self.reactions.append(e)
            if e.craftId == self.EndID:
                break

    def serialize(self) -> bytes:
        if self.reactions and self.reactions[-1].craftId == self.EndID:
            return b''.join(e.serialize() for e in self.reactions)

        return super().serialize()
