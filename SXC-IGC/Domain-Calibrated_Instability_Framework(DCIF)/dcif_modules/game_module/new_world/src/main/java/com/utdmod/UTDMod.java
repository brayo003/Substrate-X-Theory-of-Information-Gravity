package com.utdmod;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerWorldEvents;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.world.ServerWorld;

import com.utdmod.registry.ModItems;
import com.utdmod.network.TensionSyncPacket;
import com.utdmod.network.UseCrystalPacket;
import com.utdmod.core.TensionManager;
import com.utdmod.core.WorldTensionScheduler;

public class UTDMod implements ModInitializer {

    public static final String MOD_ID = "utdmod";
    public static final org.slf4j.Logger LOGGER = org.slf4j.LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitialize() {
        // Register items
        ModItems.registerModItems();
        
        // Register network packets
        TensionSyncPacket.registerReceiver();
        UseCrystalPacket.registerReceiver();
        
        // Register world scheduler
        WorldTensionScheduler.register();
        
        // Register world load event for initialization
        ServerWorldEvents.LOAD.register((server, world) -> {
            LOGGER.info("[UTDMod] World loaded: " + world.getRegistryKey().getValue());
            TensionManager.setTension(0.0); // Reset tension on world load
        });
        
        LOGGER.info("[UTDMod] Core initialization complete. Unified tick scheduler active.");
    }
}
