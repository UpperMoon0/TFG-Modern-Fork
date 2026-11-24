// TEST ONLY: actual sided GTCEu fluid capability and Kelvin steam network.
var CQA_Pos=Java.loadClass('net.minecraft.core.BlockPos');
var CQA_RL=Java.loadClass('net.minecraft.resources.ResourceLocation');
var CQA_Regs=Java.loadClass('net.minecraftforge.registries.ForgeRegistries');
var CQA_Dir=Java.loadClass('net.minecraft.core.Direction');
var CQA_Cap=Java.loadClass('net.minecraftforge.common.capabilities.ForgeCapabilities');
var CQA_Action=Java.loadClass('net.minecraftforge.fluids.capability.IFluidHandler$FluidAction');
var CQA_FluidStack=Java.loadClass('net.minecraftforge.fluids.FluidStack');
var CQA_Mod=Java.loadClass('org.valkyrienskies.clockwork.ClockworkMod');
var CQA_Extractor=Java.loadClass('org.valkyrienskies.clockwork.content.logistics.gas.generation.steam_generator.SteamGeneratorBlock');
var CQA={ticks:0,done:false,started:false};
function cqaAssert(v,msg){if(!v)throw new Error(msg);}
function cqaPlace(w,pos,id,props){
    var block=CQA_Regs.BLOCKS.getValue(new CQA_RL(id));
    cqaAssert(block && String(CQA_Regs.BLOCKS.getKey(block))===id,'Missing block '+id);
    var state=block.defaultBlockState();
    Object.keys(props||{}).forEach(function(k){
        var property=state.getBlock().getStateDefinition().getProperty(k);
        state=state.setValue(property,property.getValue(props[k]).get());
    });
    cqaAssert(w.setBlock(pos,state,3),'placement failed '+id);
    return w.getBlockEntity(pos);
}
function cqaFill(id,amount){
    var f=CQA_Regs.FLUIDS.getValue(new CQA_RL(id));
    var s=new CQA_FluidStack(f,amount);
    cqaAssert(Number(CQA.handler.fill(s,CQA_Action.EXECUTE))===amount,'source fill rejected '+id);
}
function cqaAmount(){
    var n=0;for(var i=0;i<CQA.handler.getTanks();i++) n+=Number(CQA.handler.getFluidInTank(i).getAmount());
    return n;
}
function cqaMass(){
    var node=CQA.extractor.getDuctNodePosition();
    var v=CQA.network.getGasMassAt(node).get(CQA.extractor.getSteamGas());
    return v==null?0:Number(v);
}
// Reuse the exact production definitions to avoid a stale parallel list.
function cqaAuditRecipes(w){
    var manager=w.getRecipeManager(), checked=0;
    function inspect(v,path){
        if(v===null||typeof v!=='object')return;
        if(Array.isArray(v)){v.forEach((x,i)=>inspect(x,path+'['+i+']'));return;}
        if(typeof v.item==='string')cqaAssert(CQA_Regs.ITEMS.containsKey(new CQA_RL(v.item)),path+' unknown item '+v.item);
        if(typeof v.tag==='string')cqaAssert(Ingredient.of('#'+v.tag).getItems().length>0,path+' empty item tag '+v.tag);
        if(typeof v.fluid==='string')cqaAssert(CQA_Regs.FLUIDS.containsKey(new CQA_RL(v.fluid)),path+' unknown fluid '+v.fluid);
        Object.keys(v).forEach(k=>inspect(v[k],path+'.'+k));
    }
    registerTFGClockworkNativeCompatibility({
        remove:function(filter){
            cqaAssert(!manager.byKey(new CQA_RL(filter.id)).isPresent(),'old recipe survived '+filter.id);
        },
        custom:function(definition){
            return {id:function(id){
                var recipe=manager.byKey(new CQA_RL(id));
                cqaAssert(recipe.isPresent(),'missing registered recipe '+id);
                inspect(definition,id);
                if(id.indexOf('/gas_crafting/vitriol_')!==-1){
                    var fluids=recipe.get().getFluidIngredients();
                    cqaAssert(fluids.size()===1 && Number(fluids.get(0).getRequiredAmount())===definition.ingredients[0].amount,'incorrect gas recipe fluid ingredient '+id);
                }
                checked++;
            }};
        }
    });
    cqaAssert(checked>0,'no native compatibility recipes audited');
    console.info('[CLOCKWORK_RECIPE_AUDIT_PASS] registered='+checked);
}
function cqaFail(e){CQA.done=true;console.error('[CLOCKWORK_COMPAT_FAIL] '+e+' '+(e.stack||''));}
ServerEvents.loaded(event=>{
    try {
        var w=event.server.overworld(),s=w.getSharedSpawnPos();
        cqaAuditRecipes(w);
        var x=(s.getX()>>4)*16+4,z=(s.getZ()>>4)*16+12,y=Math.min(w.getMaxBuildHeight()-8,Math.max(230,s.getY()+65));
        var p=new CQA_Pos(x,y,z);
        w.setChunkForced(x>>4,z>>4,true);
        var drum=cqaPlace(w,p,'gtceu:steel_drum',{});
        var extractor=cqaPlace(w,p.east(),'vs_clockwork:steam_generator',{face:'wall',facing:'east'});
        cqaAssert(extractor!=null,'extractor missing');
        cqaAssert(CQA_Extractor.getFacing(extractor.getBlockState())===CQA_Dir.EAST,'extractor facing');
        cqaAssert(extractor.getBlockState().canSurvive(w,p.east()),'extractor cannot survive on GT drum');
        CQA.handler=drum.getCapability(CQA_Cap.FLUID_HANDLER,CQA_Dir.EAST).orElse(null);
        cqaAssert(CQA.handler!=null,'GT drum sided fluid capability missing');
        CQA.extractor=extractor; CQA.network=CQA_Mod.INSTANCE.getKelvin(w); CQA.world=w; CQA.pos=p;
        cqaFill('minecraft:water',1000);
        CQA.started=true;
        console.info('[CLOCKWORK_COMPAT_STARTED] GT steel drum + extractor');
    }catch(e){cqaFail(e);}
});
ServerEvents.tick(event=>{
    if(!CQA.started||CQA.done)return;
    try{
        CQA.ticks++;
        if(CQA.ticks===30){
            cqaAssert(cqaAmount()===1000,'water was consumed');
            cqaAssert(cqaMass()===0,'water converted to steam');
            var water=CQA_Regs.FLUIDS.getValue(new CQA_RL('minecraft:water'));
            var drained=CQA.handler.drain(new CQA_FluidStack(water,1000),CQA_Action.EXECUTE);
            cqaAssert(Number(drained.getAmount())===1000,'water drain failed');
            cqaFill('gtceu:steam',10000);
            console.info('[CLOCKWORK_COMPAT_WATER_PASS] water=1000 unchanged');
        }
        if(CQA.ticks===130){
            var amount=cqaAmount(), mass=cqaMass();
            var node=CQA.extractor.getDuctNodePosition();
            var pressure=Number(CQA.network.getPressureAt(node));
            cqaAssert(amount<10000&&mass>0,'GT steam bridge inactive; remaining='+amount+' mass='+mass+' pressure='+pressure);
            cqaAssert(Math.abs(mass-(10000-amount)*0.001)<0.00001,'mass mismatch: '+mass+' vs '+(10000-amount)*0.001);
            cqaAssert(pressure<=2125000+1,'pressure cap exceeded '+pressure);
            console.info('[CLOCKWORK_COMPAT_STEAM_PASS] drained_mb='+(10000-amount)+' steam_kg='+mass+' pressure_pa='+pressure);
            CQA.done=true;
            console.info('[CLOCKWORK_COMPAT_PASS]');
        }
    }catch(e){cqaFail(e);}
});
