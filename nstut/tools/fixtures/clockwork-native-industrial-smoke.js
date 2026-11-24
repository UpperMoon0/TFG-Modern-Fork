// TEST ONLY: actual GT boiler, pipe, Clockwork gas flow and Greate stress.
var CIQA_Meta=Java.loadClass('com.gregtechceu.gtceu.api.machine.MetaMachine');
var CIQA_Piston=Java.loadClass('com.simibubi.create.content.kinetics.steamEngine.SteamEngineBlock');
var CIQA_GasRecipe=Java.loadClass('org.valkyrienskies.clockwork.content.logistics.gas.crafter.GasCraftingRecipe');
var CIQA_Gases=Java.loadClass('org.valkyrienskies.kelvin.impl.registry.GasTypeRegistry');
var CIQA={ticks:0,stage:0,done:false,started:false,chemDone:false,errors:[]};
function ciqaReport(name,e){
    CIQA.errors.push(name+': '+e);
    console.warn('[CLOCKWORK_INDUSTRIAL_ISSUE] '+name+': '+e+' '+(e.stack||''));
}
function ciqaComplete(){
    if(!CIQA.done||!CIQA.chemDone)return;
    if(CIQA.errors.length)console.error('[CLOCKWORK_INDUSTRIAL_FAIL] '+CIQA.errors.join('; '));
    else console.info('[CLOCKWORK_INDUSTRIAL_PASS]');
}
function ciqaPosition(w,x,y,z){
    var s=w.getSharedSpawnPos(),p=new CQA_Pos((s.getX()>>4)*16+x,Math.min(w.getMaxBuildHeight()-10,Math.max(235,s.getY()+70))+y,(s.getZ()>>4)*16+z);
    w.setChunkForced(p.getX()>>4,p.getZ()>>4,true);
    return p;
}
function ciqaGasMass(node,gas){
    var v=CIQA.network.getGasMassAt(node).get(gas);
    return v==null?0:Number(v);
}
function ciqaGas(id){return CIQA_Gases.INSTANCE.getGasType(new CQA_RL(id));}
function ciqaNear(actual,expected,label){
    cqaAssert(Math.abs(actual-expected)<0.00001,label+' expected='+expected+' actual='+actual);
}
function ciqaChemistry(){
    var w=CIQA.world, be=CIQA.crafter, basin=CIQA.basin,n=CIQA.network,pos=be.getDuctNodePosition();
    cqaAssert(n.getNodeAt(pos)!=null&&n.getNodeInfo().containsKey(pos),'uninitialized gas crafter');
    var input=basin.getInputInventory(), tank=basin.inputTank.getPrimaryHandler();
    var steam=ciqaGas('vs_clockwork:steam'), bog=ciqaGas('vs_clockwork:bog'), stellane=ciqaGas('vs_clockwork:stellane'), vitriol=ciqaGas('vs_clockwork:vitriol'), phlogiston=ciqaGas('vs_clockwork:phlogiston'), exhaust=ciqaGas('vs_clockwork:exhaust'), air=ciqaGas('kelvin:air');
    function recipe(id){return w.getRecipeManager().byKey(new CQA_RL(id)).get();}
    function heat(){
        // Direct native recipe execution fixture: establish a controlled
        // Kelvin temperature, without claiming this is a physical heater test.
        n.modTemperature(pos,825-Number(n.getTemperatureAt(pos)));
        var desired=Math.max(200000,825*Number(n.getNodeHeatCapacity(pos)));
        n.modHeatEnergy(pos,desired-Number(n.getHeatEnergy(pos)));
    }
    function apply(id,energy,inputs,outputs){
        var r=recipe(id),before=Number(n.getHeatEnergy(pos));
        cqaAssert(CIQA_GasRecipe.match(be,r),'native match rejected '+id);
        for(var i=0;i<inputs.length;i++)ciqaNear(ciqaGasMass(pos,inputs[i][0]),inputs[i][1],'match mutated input');
        cqaAssert(CIQA_GasRecipe.apply(be,r),'native apply rejected '+id);
        for(var i=0;i<outputs.length;i++)ciqaNear(ciqaGasMass(pos,outputs[i][0]),outputs[i][1],id+' gas');
        cqaAssert(Math.abs(Number(n.getHeatEnergy(pos))-before-energy)<0.01,id+' energy accounting');
        console.info('[CLOCKWORK_CHEMISTRY_STAGE_PASS] '+id+' energy='+energy);
    }
    // Eliminate ambient air from the controlled node, then supply native
    // gasification with real coal and 50 g steam.
    n.modGasMass(pos,air,-ciqaGasMass(pos,air));
    n.modGasMass(pos,steam,0.05-ciqaGasMass(pos,steam));
    heat();
    input.setStackInSlot(0,Item.of('minecraft:charcoal'));
    apply('vs_clockwork:gas_crafting/coal_gasification',0,[[steam,0.05]],[[steam,0],[bog,0.03],[stellane,0.03],[exhaust,0.05]]);
    cqaAssert(input.getStackInSlot(0).isEmpty(),'coal not consumed');
    // Supply the additional steam and bog required by reforming.
    n.modGasMass(pos,steam,0.05);
    n.modGasMass(pos,bog,0.02);
    heat();
    input.setStackInSlot(0,Item.of('gtceu:wrought_iron_nugget'));
    apply('tfg:clockwork/compat/gas_crafting/methane_reforming',-165000,[[steam,0.05],[bog,0.05]],[[steam,0],[bog,0],[stellane,0.08],[exhaust,0.10]]);
    cqaAssert(input.getStackInSlot(0).isEmpty(),'reforming reagent not consumed');
    // Actual basin fluid stack, not just a serializer check.
    heat();
    tank.setFluid(Fluid.of('gtceu:sulfuric_acid',99));
    var acidRecipe=recipe('tfg:clockwork/compat/gas_crafting/vitriol_awkward');
    cqaAssert(!CIQA_GasRecipe.match(be,acidRecipe),'99 mB incorrectly satisfies 100 mB');
    cqaAssert(Number(tank.getFluidAmount())===99,'negative match consumed acid');
    tank.setFluid(Fluid.of('gtceu:sulfuric_acid',100));
    apply('tfg:clockwork/compat/gas_crafting/vitriol_awkward',10000,[],[[vitriol,0.05]]);
    cqaAssert(Number(tank.getFluidAmount())===0,'acid not consumed');
    heat();
    input.setStackInSlot(0,Item.of('beneath:cursecoal'));
    apply('tfg:clockwork/compat/gas_crafting/phlogiston',1000,[[stellane,0.08],[vitriol,0.05]],[[stellane,0.078],[vitriol,0.049],[phlogiston,0.003]]);
    cqaAssert(input.getStackInSlot(0).isEmpty(),'phlogiston reagent not consumed');
    console.info('[CLOCKWORK_CHEMISTRY_PASS]');
}
ServerEvents.loaded(event=>{
    CIQA.world=event.server.overworld();
    CIQA.network=CQA_Mod.INSTANCE.getKelvin(CIQA.world);
    var w=CIQA.world;
    try{
        var p=ciqaPosition(w,34,0,3);
        cqaPlace(w,p,'gtceu:hp_steam_solid_boiler',{});
        var b=CIQA_Meta.getMachine(w,p);
        cqaAssert(b!=null,'GT boiler missing');
        b.setFrontFacing(CQA_Dir.NORTH);
        var capacity=Number(b.waterTank.getTankCapacity(0));
        b.waterTank.setFluidInTank(0,Fluid.of('minecraft:water',capacity));
        cqaAssert(Number(b.waterTank.getFluidInTank(0).getAmount())===capacity,'water input rejected');
        cqaAssert(b.fuelHandler.insertItem(0,Item.of('minecraft:charcoal',16),false).isEmpty(),'boiler fuel rejected');
        var pipe=cqaPlace(w,p.east(),'gtceu:steel_normal_fluid_pipe',{});
        pipe.setConnection(CQA_Dir.WEST,true,false);
        pipe.setConnection(CQA_Dir.EAST,true,false);
        var ex=cqaPlace(w,p.east(2),'vs_clockwork:steam_generator',{face:'wall',facing:'east'});
        cqaAssert(ex.getBlockState().canSurvive(w,p.east(2)),'extractor cannot attach to connected GT pipe');
        var duct=cqaPlace(w,p.east(3),'vs_clockwork:duct',{});
        var engine=cqaPlace(w,p.east(4),'vs_clockwork:gas_engine',{axis:'x'});
        cqaPlace(w,p.east(5),'vs_clockwork:exhaust',{facing:'east'});
        var pistonPos=p.east(4).north(), shaftPos=p.east(4).north(3);
        cqaPlace(w,shaftPos,'greate:steel_shaft',{axis:'x'});
        var piston=cqaPlace(w,pistonPos,'create:steam_engine',{face:'wall',facing:'north'});
        cqaAssert(CIQA_Piston.getShaftPos(piston.getBlockState(),pistonPos).equals(shaftPos),'wrong piston geometry');
        var consumerPos=shaftPos.east();
        cqaPlace(w,consumerPos,'greate:steel_cogwheel',{axis:'x'});
        CIQA.boiler=b; CIQA.water=capacity; CIQA.pipe=pipe; CIQA.extractor=ex; CIQA.engine=engine; CIQA.duct=duct;
        CIQA.pistonPos=pistonPos; CIQA.shaftPos=shaftPos; CIQA.consumerPos=consumerPos;
        CIQA.started=true;
        console.info('[CLOCKWORK_KINETICS_STARTED] actual boiler + connected steel pipe + extractor + exhaust');
    }catch(e){ciqaReport('kinetics setup',e);CIQA.done=true;}
    try{
        var p=ciqaPosition(w,34,0,9);
        cqaPlace(w,p.below(2),'create:blaze_burner',{blaze:'kindled'});
        CIQA.basin=cqaPlace(w,p.below(),'create:basin',{});
        CIQA.crafter=cqaPlace(w,p,'vs_clockwork:gas_crafter',{});
    }catch(e){ciqaReport('chemistry setup',e);CIQA.chemDone=true;}
    ciqaComplete();
});
ServerEvents.tick(event=>{
    if(CIQA.done&&CIQA.chemDone)return;
    CIQA.ticks++;
    if(!CIQA.chemDone&&CIQA.ticks>=20){
        try{ciqaChemistry();}catch(e){ciqaReport('chemistry',e);}
        CIQA.chemDone=true;ciqaComplete();
    }
    if(!CIQA.started||CIQA.done)return;
    try{
        var w=CIQA.world, b=CIQA.boiler, e=CIQA.engine;
        var shaft=w.getBlockEntity(CIQA.shaftPos), consumer=w.getBlockEntity(CIQA.consumerPos);
        if(CIQA.stage===0){
            var rpm=shaft?Math.abs(Number(shaft.getSpeed())):0;
            var flow=Number(e.getRawFlowRate()), eff=Number(e.getEngineEfficiency());
            if(rpm>0&&flow>0&&eff>0&&consumer&&Math.abs(Number(consumer.getSpeed()))>0){
                cqaAssert(Number(b.getCurrentTemperature())>0&&Number(b.waterTank.getFluidInTank(0).getAmount())<CIQA.water,'boiler did not consume water');
                cqaAssert(Number(shaft.calculateAddedStressCapacity())>0&&!shaft.isOverStressed(),'no usable stress');
                cqaAssert(Math.abs(Number(consumer.getSpeed()))===rpm,'consumer speed mismatch');
                console.info('[CLOCKWORK_KINETICS_DRIVE_PASS] rpm='+rpm+' flow='+flow+' efficiency='+eff+' stress='+shaft.calculateAddedStressCapacity());
                b.getRecipeLogic().setWorkingEnabled(false);
                CIQA.pipe.setConnection(CQA_Dir.WEST,false,false);
                CIQA.stage=1; CIQA.shutdownTick=CIQA.ticks;
            }else if(CIQA.ticks>1800)throw new Error('no real rotation: temperature='+b.getCurrentTemperature()+' gas='+ciqaGasMass(CIQA.extractor.getDuctNodePosition(),CIQA.extractor.getSteamGas())+' flow='+flow+' efficiency='+eff+' rpm='+rpm);
        }else if(CIQA.stage===1){
            if(shaft&&Math.abs(Number(shaft.getSpeed()))===0&&Number(e.getEngineEfficiency())===0){
                cqaAssert(!consumer||Number(consumer.getSpeed())===0,'consumer still driven after steam shutdown');
                console.info('[CLOCKWORK_KINETICS_SHUTDOWN_PASS]');
                w.removeBlock(CIQA.pistonPos,false);
                CIQA.stage=2;CIQA.removedTick=CIQA.ticks;
            }else if(CIQA.ticks-CIQA.shutdownTick>600)throw new Error('steam shutdown failed');
        }else if(CIQA.stage===2&&CIQA.ticks-CIQA.removedTick>=40){
            cqaAssert(String(CQA_Regs.BLOCKS.getKey(w.getBlockState(CIQA.shaftPos).getBlock()))==='greate:steel_shaft','shaft tier not restored');
            console.info('[CLOCKWORK_KINETICS_PASS] steel shaft restored');
            CIQA.done=true;ciqaComplete();
        }
    }catch(e){ciqaReport('kinetics',e);CIQA.done=true;ciqaComplete();}
});
