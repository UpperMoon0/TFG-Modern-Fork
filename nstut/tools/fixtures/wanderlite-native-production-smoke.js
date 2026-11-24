// TEST ONLY: native recipe application and ticking HV machines.
var WQA_Pos = Java.loadClass('net.minecraft.core.BlockPos');
var WQA_RL = Java.loadClass('net.minecraft.resources.ResourceLocation');
var WQA_Regs = Java.loadClass('net.minecraftforge.registries.ForgeRegistries');
var WQA_Meta = Java.loadClass('com.gregtechceu.gtceu.api.machine.MetaMachine');
var WQA_Basin = Java.loadClass('electrolyte.greate.content.processing.basin.TieredBasinRecipe');
var WQA_Grid = Java.loadClass('com.simibubi.create.content.kinetics.crafter.MechanicalCraftingInventory');
var WQA_Grouped = Java.loadClass('com.simibubi.create.content.kinetics.crafter.RecipeGridHandler$GroupedItems');
var WQA_RecipeGrid = Java.loadClass('com.simibubi.create.content.kinetics.crafter.RecipeGridHandler');
var WQA_Tag = Java.loadClass('net.minecraft.nbt.CompoundTag');
var WQA_ListTag = Java.loadClass('net.minecraft.nbt.ListTag');
var WQA = {done:false, stage:0, ticks:0, totalEU:0, machines:[], inputs:0, initial:0};
function wqAssert(v,msg) { if (!v) throw new Error(msg); }
function wqFail(e) { WQA.done=true; console.error('[WANDERLITE_NATIVE_FAIL] '+e+' '+(e.stack||'')); }
function wqBlock(world,pos,id) {
  var b=WQA_Regs.BLOCKS.getValue(new WQA_RL(id));
  wqAssert(b && String(WQA_Regs.BLOCKS.getKey(b))===id,'missing '+id);
  wqAssert(world.getBlockState(pos).isAir(),'occupied '+pos);
  world.setBlock(pos,b.defaultBlockState(),3);
}
function wqCount(handler,id) {
  var n=0; for(var i=0;i<handler.getSlots();i++) {
    var s=handler.getStackInSlot(i); if(!s.isEmpty() && String(s.id)===id) n+=s.count;
  } return n;
}
function wqInsert(handler,slot,id,n) {
  var rest=handler.insertItem(slot,Item.of(id,n),false);
  wqAssert(rest.isEmpty(),'rejected item '+id+' '+rest);
}
function wqFluid(handler,slot,id,n) {
  wqAssert(handler.getTankCapacity(slot)>=n,'tank too small '+id);
  handler.setFluidInTank(slot,Fluid.of(id,n));
  wqAssert(handler.getFluidInTank(slot).getAmount()===n,'fluid rejected '+id);
}
function wqStart(index) {
  WQA.stage=index; WQA.ticks=0; WQA.inputs=0; WQA.processingStart=-1;
  var m=WQA.machines[index]; WQA.initial=Number(m.energyContainer.getEnergyStored());
}
function wqCost(m,expected) {
  var used=WQA.initial+WQA.inputs-Number(m.energyContainer.getEnergyStored());
  wqAssert(used===expected,'energy mismatch stage '+WQA.stage+' expected '+expected+' got '+used);
  WQA.totalEU+=used;
  console.info('[WANDERLITE_STAGE_PASS] stage='+WQA.stage+' eu='+used);
}
ServerEvents.loaded(event=>{
 try {
  var w=event.server.overworld(), s=w.getSharedSpawnPos();
  var x=(s.getX()>>4)*16+6,z=(s.getZ()>>4)*16+6,y=Math.min(w.getMaxBuildHeight()-8,Math.max(215,s.getY()+50))+4;
  var ids=['gtceu:hv_mixer','gtceu:hv_chemical_reactor','gtceu:hv_autoclave'];
  for(var i=0;i<3;i++){
    var p=new WQA_Pos(x+3*i,y,z);
    w.setChunkForced(p.getX()>>4,p.getZ()>>4,true);
    wqBlock(w,p,ids[i]);
    var m=WQA_Meta.getMachine(w,p);
    wqAssert(m && m.getTier()===3,'HV machine missing '+ids[i]);
    m.getRecipeLogic().setWorkingEnabled(false);
    WQA.machines.push(m);
  }
  WQA.world=w; WQA.basinPos=new WQA_Pos(x,y,z+4);
  wqBlock(w,WQA.basinPos,'create:basin');
  var mix=WQA.machines[0];
  wqInsert(mix.importItems,0,'tfg:igneous_felsic_dust',16);
  wqInsert(mix.importItems,1,'tfg:metamorphic_dust',8);
  wqInsert(mix.importItems,2,'minecraft:amethyst_shard',4);
  wqFluid(mix.importFluids,0,'gtceu:distilled_water',4000);
  wqStart(0); mix.getRecipeLogic().setWorkingEnabled(true);
  WQA.started=true;
 } catch(e){ wqFail(e); }
});
ServerEvents.tick(event=>{
 if(!WQA.started||WQA.done)return;
 try {
  WQA.ticks++;
  var m=WQA.machines[WQA.stage];
  var e=m.energyContainer, before=Number(e.getEnergyStored());
  if(before<960){e.changeEnergy(960-before);WQA.inputs+=Number(e.getEnergyStored())-before;}
  var logic=m.getRecipeLogic();
  var duration=[600,800,1600][WQA.stage];
  if(WQA.processingStart<0 && (logic.getProgress()>0 || String(logic.getStatus())==='WORKING')){
    WQA.processingStart=WQA.ticks;
    console.info('[WANDERLITE_STAGE_STARTED] stage='+WQA.stage+' ticks='+WQA.ticks);
  }
  if((WQA.processingStart<0 && WQA.ticks>300) ||
     (WQA.processingStart>=0 && WQA.ticks-WQA.processingStart>duration+200) ||
     WQA.ticks>duration+500)
    throw new Error('stage timeout '+WQA.stage+' progress='+logic.getProgress()+
      ' duration='+logic.getDuration()+' status='+logic.getStatus()+' reason='+logic.getWaitingReason());
  if(WQA.stage===0 && m.exportFluids.getFluidInTank(0).getAmount()===8000){
    wqCost(m,288000);
    wqAssert(wqCount(m.importItems,'tfg:igneous_felsic_dust')===0 && wqCount(m.importItems,'tfg:metamorphic_dust')===0 && wqCount(m.importItems,'minecraft:amethyst_shard')===0,'mixer inputs remain');
    wqAssert(m.importFluids.getFluidInTank(0).getAmount()===0,'mixer water remains');
    // Snapshot the actual output's identity and quantity before touching either tank.
    // KubeJS wraps FluidStacks; do not pass an aliased or wrapped tank-owned
    // FluidStack to the other machine. Check both sides of the conserved transfer.
    var product=m.exportFluids.getFluidInTank(0);
    var fluidId=String(WQA_Regs.FLUIDS.getKey(product.getFluid()));
    var amount=Number(product.getAmount());
    wqAssert(fluidId==='tfg:wanderlite_silicate_slurry' && amount===8000,'wrong mixer product');
    logic.setWorkingEnabled(false);
    var next=WQA.machines[1];
    wqAssert(next.importFluids.getFluidInTank(0).getAmount()===0,'reactor tank not empty');
    wqFluid(next.importFluids,0,fluidId,amount);
    wqAssert(String(WQA_Regs.FLUIDS.getKey(next.importFluids.getFluidInTank(0).getFluid()))===fluidId,'reactor transfer type mismatch');
    wqAssert(m.exportFluids.getFluidInTank(0).getAmount()===amount,'source changed during copy');
    m.exportFluids.setFluidInTank(0,Fluid.of('minecraft:empty',0));
    wqAssert(m.exportFluids.getFluidInTank(0).getAmount()===0 &&
      next.importFluids.getFluidInTank(0).getAmount()===amount,'fluid conservation failed');
    console.info('[WANDERLITE_TRANSFER_PASS] fluid='+fluidId+' amount='+amount+' source=0 destination='+amount);
    wqInsert(next.importItems,0,'minecraft:redstone',8);
    wqFluid(next.importFluids,1,'gtceu:oxygen',1000);
    wqStart(1); next.getRecipeLogic().setWorkingEnabled(true);
  } else if(WQA.stage===1){
    if(WQA.ticks===40){
      wqAssert(logic.getProgress()===0 && wqCount(m.importItems,'minecraft:redstone')===8,'reactor ran without pearl');
      wqInsert(m.importItems,1,'tfg:vitrified_pearl',2);
      console.info('[WANDERLITE_NEGATIVE_PASS] missing_pearl');
    }
    if(wqCount(m.exportItems,'tfg:charged_wanderlite_precursor_dust')===8){
      wqCost(m,384000);
      wqAssert(wqCount(m.importItems,'tfg:vitrified_pearl')===2,'pearls consumed');
      wqAssert(wqCount(m.importItems,'minecraft:redstone')===0,'redstone not consumed');
      wqAssert(m.importFluids.getFluidInTank(0).getAmount()===0 && m.importFluids.getFluidInTank(1).getAmount()===0,'reactor fluid remains');
      var dust=m.exportItems.getStackInSlot(0);
      var dustId=String(dust.id), dustCount=Number(dust.count);
      wqAssert(dustId==='tfg:charged_wanderlite_precursor_dust' && dustCount===8,'wrong precursor output');
      logic.setWorkingEnabled(false);
      var next=WQA.machines[2];
      wqAssert(wqCount(next.importItems,dustId)===0,'autoclave already contains precursor');
      wqInsert(next.importItems,0,dustId,dustCount);
      var removed=m.exportItems.extractItemInternal(0,dustCount,false);
      wqAssert(wqCount(m.exportItems,dustId)===0 && wqCount(next.importItems,dustId)===dustCount,'precursor conservation failed');
      console.info('[WANDERLITE_TRANSFER_PASS] item='+dustId+' amount='+dustCount+' source=0 destination='+dustCount);
      wqFluid(next.importFluids,0,'gtceu:distilled_water',4000);
      wqStart(2); next.getRecipeLogic().setWorkingEnabled(true);
    }
  } else if(WQA.stage===2){
    if(WQA.ticks===40){
      wqAssert(logic.getProgress()===0 && wqCount(m.importItems,'tfg:charged_wanderlite_precursor_dust')===8,'autoclave ran without seed');
      wqInsert(m.importItems,1,'vs_clockwork:wanderlite_crystal',1);
      console.info('[WANDERLITE_NEGATIVE_PASS] missing_seed');
    }
    if(wqCount(m.exportItems,'vs_clockwork:wanderlite_deepslate_ore')===1){
      wqCost(m,768000);
      wqAssert(wqCount(m.importItems,'vs_clockwork:wanderlite_crystal')===1,'seed consumed');
      wqAssert(wqCount(m.importItems,'tfg:charged_wanderlite_precursor_dust')===0 && m.importFluids.getFluidInTank(0).getAmount()===0,'autoclave inputs remain');
      wqAssert(WQA.totalEU===1440000,'total energy mismatch');
      logic.setWorkingEnabled(false);
      console.info('[WANDERLITE_HV_PASS] eu='+WQA.totalEU+' ore=1 pearls=2 seed=1');
      var w=WQA.world, basin=w.getBlockEntity(WQA.basinPos), manager=w.getRecipeManager();
      var recipe=manager.byKey(new WQA_RL('tfg:clockwork/steam/wanderlite_trace_recovery')).get();
      wqAssert(recipe.getRecipeTier()===1,'steam tier mismatch');
      var input=basin.getInputInventory(), output=basin.getOutputInventory(), traces=0;
      var traceTags=new WQA_ListTag();
      for(var i=0;i<16;i++){
        input.setStackInSlot(0,Item.of('gtceu:raw_graphite',4));
        input.setStackInSlot(1,Item.of('tfc:ore/normal_magnetite',4));
        input.setStackInSlot(2,Item.of('minecraft:amethyst_shard'));
        wqAssert(!WQA_Basin.match(basin,recipe,0),'tier 0 accepted');
        wqAssert(WQA_Basin.match(basin,recipe,1),'steam basin mismatch batch '+i);
        wqAssert(WQA_Basin.apply(basin,recipe),'steam basin apply failed '+i);
        wqAssert(input.getStackInSlot(0).isEmpty() && input.getStackInSlot(1).isEmpty() && input.getStackInSlot(2).isEmpty(),'steam input remains');
        wqAssert(wqCount(output,'tfg:wanderlite_trace')===1,'trace output missing');
        for(var j=0;j<output.getSlots();j++){
          var st=output.extractItem(j,64,false);
          if(!st.isEmpty()){
            wqAssert(String(st.id)==='tfg:wanderlite_trace' && st.count===1,'wrong trace');
            var entry=new WQA_Tag();
            entry.putInt('x',traces%4); entry.putInt('y',Math.floor(traces/4));
            entry.put('item',st.serializeNBT()); traceTags.add(entry); traces++;
          }
        }
      }
      wqAssert(traces===16,'wrong trace count');
      console.info('[WANDERLITE_STEAM_MIX_PASS] traces='+traces+' consumed_graphite=64 consumed_magnetite=64 consumed_amethyst=16');
      // Use Create's actual serialized grouped items, not a vanilla crafting table
      // inventory (which MechanicalCraftingRecipe deliberately rejects).
      var groupTag=new WQA_Tag(); groupTag.put('Grid',traceTags);
      var grouped=WQA_Grouped.read(groupTag); grouped.calcStats();
      var grid=new WQA_Grid(grouped);
      wqAssert(grid.getWidth()===4 && grid.getHeight()===4 && grid.getContainerSize()===16,'wrong native mechanical grid size');
      var craft=manager.byKey(new WQA_RL('tfg:clockwork/steam/consolidate_wanderlite_traces')).get();
      wqAssert(craft.matches(grid,w),'mechanical grid mismatch');
      // Exercise the same native lookup used by the crafter's real grouped-grid path.
      var crystal=WQA_RecipeGrid.tryToApplyRecipe(w,grouped);
      wqAssert(String(crystal.id)==='vs_clockwork:wanderlite_crystal' && crystal.count===1,'wrong crafted crystal');
      console.info('[WANDERLITE_STEAM_PASS] graphite=64 magnetite=64 amethyst=16 traces=16 crystal=1');
      WQA.done=true;
      console.info('[WANDERLITE_NATIVE_PASS]');
    }
  }
 } catch(e){wqFail(e);}
});
