// TEST-ONLY SCRIPT. Must never ship or be included in production KubeJS.
// Calls native Clockwork PhysicsInfuserBlockEntity.startAssembly against a
// deliberately disconnected 3x3 wooden hull in a disposable server world.
var CWQA_BlockPos = Java.loadClass('net.minecraft.core.BlockPos');
var CWQA_CompoundTag = Java.loadClass('net.minecraft.nbt.CompoundTag');
var CWQA_ListTag = Java.loadClass('net.minecraft.nbt.ListTag');
var CWQA_ItemStack = Java.loadClass('net.minecraft.world.item.ItemStack');
var CWQA_Blocks = Java.loadClass('net.minecraft.world.level.block.Blocks');
var CWQA_ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation');
var CWQA_ForgeRegistries = Java.loadClass('net.minecraftforge.registries.ForgeRegistries');
var CWQA = {started: false, done: false, ticks: 0, infuser: null, world: null, pos: null};

function cwqaFail(why) {
    if (CWQA.done) return;
    CWQA.done = true;
    console.error('[CLOCKWORK_GAMEPLAY_FAIL] ' + String(why));
}
ServerEvents.loaded(event => {
    try {
        var qaLevel = event.server.overworld();
        if (!qaLevel) throw new Error('Overworld not available');
        var spawn = qaLevel.getSharedSpawnPos();
        var x = (spawn.getX() >> 4) * 16 + 6;
        var z = (spawn.getZ() >> 4) * 16 + 6;
        var y = Math.min(qaLevel.getMaxBuildHeight() - 7, Math.max(215, spawn.getY() + 50));
        var origin = new CWQA_BlockPos(x, y, z);
        var infuserPos = new CWQA_BlockPos(x + 6, y, z);
        // getChunkAt only loads a chunk; it does not guarantee the native
        // block entity ticker runs without players. Force both chunks into
        // the ticking level for this disconnected headless QA fixture.
        qaLevel.setChunkForced(origin.getX() >> 4, origin.getZ() >> 4, true);
        qaLevel.setChunkForced(infuserPos.getX() >> 4, infuserPos.getZ() >> 4, true);
        qaLevel.getChunkAt(origin);
        qaLevel.getChunkAt(infuserPos);
        // Validate the blank isolated fixture before touching any blocks.
        for (var dx = -1; dx <= 9; dx++) for (var dz = -1; dz <= 4; dz++) {
            for (var dy = -1; dy <= 2; dy++) {
                var testPos = new CWQA_BlockPos(x + dx, y + dy, z + dz);
                if (!qaLevel.getBlockState(testPos).isAir())
                    throw new Error('Fixture position not empty: ' + testPos);
            }
        }
        // Deterministically construct disconnected survival-buildable blocks.
        for (var dx = 0; dx < 3; dx++) for (var dz = 0; dz < 3; dz++)
            qaLevel.setBlock(new CWQA_BlockPos(x + dx, y, z + dz),
                CWQA_Blocks.OAK_PLANKS.defaultBlockState(), 3);

        var infuserBlock = CWQA_ForgeRegistries.BLOCKS.getValue(
            new CWQA_ResourceLocation('vs_clockwork', 'physics_infuser'));
        if (!infuserBlock) throw new Error('Physics Infuser registry entry missing');
        qaLevel.setBlock(infuserPos, infuserBlock.defaultBlockState(), 3);
        var infuser = qaLevel.getBlockEntity(infuserPos);
        if (!infuser || !String(infuser.getClass().getName()).includes('PhysicsInfuserBlockEntity'))
            throw new Error('Physics Infuser native block entity missing');
        if (infuser.startAssembly(null))
            throw new Error('Infuser erroneously assembled without Wanderwand');

        var wandItem = CWQA_ForgeRegistries.ITEMS.getValue(
            new CWQA_ResourceLocation('vs_clockwork', 'wanderwand'));
        if (!wandItem) throw new Error('Wanderwand item missing');
        var wand = new CWQA_ItemStack(wandItem);
        var tag = new CWQA_CompoundTag();
        var selection = new CWQA_CompoundTag();
        var list = new CWQA_ListTag();
        var box = new CWQA_CompoundTag();
        box.putLong('lowerCorner', origin.asLong());
        box.putLong('upperCorner', new CWQA_BlockPos(x + 3, y + 1, z + 3).asLong());
        list.add(box);
        selection.put('AABBSet', list);
        tag.put('selectedBlocks', selection);
        tag.putString('selectionDimension', 'minecraft:overworld');
        // KubeJS 2001.6 exposes ItemStack NBT through withNBT, not setTag.
        wand = Item.of('vs_clockwork:wanderwand').withNBT(tag);
        infuser.getInventory().set(0, wand);
        infuser.setChanged();

        CWQA.infuser = infuser;
        CWQA.world = qaLevel;
        CWQA.pos = origin;
        if (!infuser.startAssembly(null))
            throw new Error('Native Physics Infuser rejected a selected 3x3 hull');
        if (infuser.getRegions().size() !== 1)
            throw new Error('Expected exactly one disconnected region');
        CWQA.started = true;
        console.info('[CLOCKWORK_GAMEPLAY_STARTED] native_infuser=true selected_blocks=9');
    } catch (e) {
        cwqaFail('fixture setup: ' + String(e) + ' / ' + String(e.stack || ''));
    }
});

ServerEvents.tick(event => {
    if (!CWQA.started || CWQA.done) return;
    try {
        CWQA.ticks++;
        if (CWQA.ticks === 20) CWQA.infuser.skipAssembly();
        var region = CWQA.infuser.getRegions().get(0);
        if (region.getShipId() >= 0) {
            // The actual ship assembly moved the original hull blocks.
            if (!CWQA.world.getBlockState(CWQA.pos).isAir())
                throw new Error('Native assembler claims ship but original hull remains');
            CWQA.done = true;
            console.info('[CLOCKWORK_GAMEPLAY_PASS] ship_id=' + region.getShipId()
                + ' ticks=' + CWQA.ticks + ' hull_blocks=9');
        } else if (CWQA.ticks > 500) {
            cwqaFail('Native ship assembly did not complete within 500 server ticks; impacted=' + CWQA.infuser.getImpacted() + ' assembling=' + CWQA.infuser.getAssembling());
        }
    } catch (e) {
        cwqaFail('native ship tick: ' + String(e) + ' / ' + String(e.stack || ''));
    }
});
