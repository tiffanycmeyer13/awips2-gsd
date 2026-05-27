/**
 * This software was developed and / or modified by the
 * National Oceanic and Atmospheric Administration (NOAA),
 * Global Systems Laboratory (GSL),
 * Evaluation & Decision Support Division (EDS),
 * Weather Information Systems Evolution Branch (WISE)
 *
 * Address: Department of Commerce Boulder Labs, 325 Broadway, Boulder, CO 80305
 */
package gov.noaa.gsl.common.dataplugin.pem;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.SortedSet;
import java.util.TreeSet;

import com.raytheon.uf.common.time.TimeRange;

/**
 * The manager of PhysicalEvents. The PEM delegates most requests to
 * IPhysicalEventDaos by PhysicalEventType. So for example, to retrieve a
 * PhysicalEvent of type SEISMIC, the PEM will delegate to the appropriate DAO.
 * The reason for this design was so that PhysicalEvents of different types can
 * come from different data sources. TBD as to whether or not that was a good
 * design decision. See {@link PEMVizBundleActivator} for how the PEM gets
 * configured with DAOs.
 *
 * The PEM can be implemented as either a physical or conceptual container for
 * PhysicalEvents. In the case of physical, the PEM will actually store or cache
 * the PhysicalEvents, and the caching strategy could either be lazy or eager.
 * In contrast with a conceptual implementation, the PEM will not cache any
 * PhysicalEvents and all getter requests will be on-demand and pass thru
 * straight to the DAOs.
 *
 * The PEM manages a set of PhysicalEvents according to the PEM's properties.
 * The properties such as the timeWindow, activeOption, and typeFilters define
 * that set of PhysicalEvents that will be "contained" within the PEM. So for
 * example, the PEM might have a 1 day time window, a filter for Seismic Events,
 * and an activeOption of ActiveOnly. THis would mean the PEM would only expose
 * PhysicalEvents that match those conditions.
 *
 * On the other hand, someone might want to access the PhysicalEvent database
 * without applying those property conditions. To do that, I have exposed the
 * IPhysicalEventDaos, so that clients (such as the HID or the Tsunami Message
 * Tool) can use the the DAOs directly to query for what is in the PhysicalEvent
 * database.
 *
 * <pre>
 * LAZY CACHE - Physical
 *
 *   Startup: setDirty ( true )
 *   Setter: setDirty( true ), fireEventsChanged, firePropertyChanged
 *   Getter: if( isDirty() ), retrieveEvents / Ids
 *   Notified by child DAO: setDirty( true ), fireEventsChanged
 *
 * EAGER CACHE - Physical = CURRENT IMPLEMENTATION.
 *
 *   Startup: retrieveEvents / Ids, fireEventsChanged, firePropertyChanged
 *   Setter: retrieveEvents / Ids, fireEventsChanged, firePropertyChanged
 *   Getter: return Events / Ids
 *   Notified by child DAO: retrieveEvents / Ids, fireEventsChanged
 *
 * NO CACHE / ON DEMAND - Conceptual
 *
 *   Startup: Noop
 *   Setter: fireEventsChanged (?), firePropertyChanged
 *   Getter: return Events / Ids
 *   Notified by child DAO: fireEventsChanged
 *
 * </pre>
 *
 * The difficulty with the Lazy and NoCache methods is that those
 * implementations would only actually request the physical events on demand (ie
 * when getPhysicalEvents(...) is called). Hence, just setting a
 * property/constraint such as setTimeRange() or setFilter() would not retrieve
 * physical events. Therefore, listeners would NOT be notified that
 * physicalEventsChanged() when one of the PEM properties (eg timeRange, filter)
 * changed, since the PEM never retrieved a new set and has no clue that the set
 * may have changed.
 *
 * That being said, there are two solutions to this that I can think of. (1) The
 * PEM fires physicalEventsChanged() when a property is set, regardless. By
 * doing this, the listeners will be notified and can requery the PEM for the
 * new set of PhysicalEvents, if indeed they have changed. (2) The burden is put
 * on the listeners, such that when they might call setTimeRange or setFilter,
 * they should also call getPhysicalEvents() to refresh their set of
 * PhysicalEvents. This approach sort of violates the contract that listeners
 * will be notified of physicalEventsChanged (because they wont be notified if a
 * property/constraint was set on the PEM, but would only be notified if an EDEX
 * side change occurs).
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 * Date         Ticket#    Engineer          Description
 * ------------ ---------- ----------------- --------------------------
 * Dec 13, 2021        Robert.Weingruber     Initial Creation
 *
 * </pre>
 *
 * @author robert.weingruber
 * @version 1.0
 */
public class PhysicalEventManager {

    public enum SelectionMode {
        SINGLE,
        MULTIPLE
    }

    /**
     * Make this List threadsafe, since EDEX may notifies the DAOs on different
     * threads, thereby entering notification methods within the PEM on
     * different threads.
     *
     * The list of listeners that the PEM will notify upon PhysicalEvent
     * changes.
     */
    private List<IPhysicalEventMgrListener> listeners = Collections
            .synchronizedList(new ArrayList<>());

    /**
     * A Map of PhysicalEventType to the DAO which is responsible for retrieval
     * of PhysicalEvents of that type.
     */
    private Map<PhysicalEventType, IPhysicalEventDao> daoMap = new HashMap<>();

    /**
     * The internal listener listening for notifications received from the DAOs.
     */
    private IPhysicalEventDaoListener daoListener = new PhysicalEventDaoListener();

    /**
     * TODO It might be better to implement the cache as a
     * Map<PhysicalEventType, Map<CustomId, IPhysicalEvent>> since delete /
     * update has to go thru the event by customId
     */
    private Map<PhysicalEventType, List<IPhysicalEvent>> phyEventCache = new HashMap<>();

    /**
     * The first time a getter is called, the cache may not have been
     * initialized yet (ie refreshPhysicalEvents() may not have been called
     * yet). So we need to make sure it's called before the getter, so with the
     * getters, refreshPhysicalEvents if we have not yet been initialized.
     */
    private boolean isCacheInitialized = false;

    /**
     * A property representing the time window of interest for the PEM.
     * PhysicalEvent managed by the PEM will be restricted to PhysicalEvents
     * whose dataTime.refTime is within this timeWindow (start and end times
     * inclusive). null is a valid value, meaning all time.
     */
    private TimeRange timeWindow = null;

    /**
     * A property representing whether the PEM should restrict its retrievals /
     * management of PhysicalEvents to active, inactive, or all events.
     */
    private ActiveOption activeOption = ActiveOption.ACTIVE_ONLY;

    /**
     * A property representing filters that allow the PEM to restrict its
     * management of PhysicalEvents to those of a certain type or types. For
     * example, if there are two filters PhysicalEventType.SEISMIC and
     * PhysicalEventType.VOLCANIC, then the PEM will only retrieve and/or manage
     * SEISMIC and VOLCANIC PhysicalEvents. An empty list means no filters, and
     * PhysicalEvents of all types will be available.
     */
    private List<PhysicalEventType> typeFilters = new ArrayList<>();

    /*
     * =========================================================================
     * View UI Helper Stuff
     * =========================================================================
     */
    private SelectionMode selectionMode = SelectionMode.SINGLE;

    private Set<String> selectedEventIds = new HashSet<>();

    /**
     * Singleton instance
     */
    private static PhysicalEventManager instance = null;

    /**
     * Simplistic singleton pattern, such as this, is not really threadsafe
     * folks.
     *
     * @return
     */
    public static PhysicalEventManager getInstance() {
        if (instance == null) {
            instance = new PhysicalEventManager();
        }
        return instance;
    }

    protected PhysicalEventManager() {
    }

    /*
     * =========================================================================
     * PEM Property-related methods.
     * =========================================================================
     */

    /**
     * May return null, meaning all time.
     *
     * @return
     */
    public TimeRange getTimeWindow() {
        if (timeWindow == null) {
            return null;
        }
        return timeWindow.clone();
    }

    public void setTimeWindow(TimeRange newTimeRange) {

        // No change means nothing to do
        if ((this.timeWindow == null && newTimeRange == null)
                || (this.timeWindow.equals(newTimeRange))) {
            return;
        }

        this.timeWindow = newTimeRange;
        refreshPhysicalEvents();
        fireTimeWindowChanged(this.timeWindow);
    }

    public ActiveOption getActiveOption() {
        return activeOption;
    }

    public void setActiveOption(ActiveOption activeOption) {
        // No change means nothing to do
        if (activeOption == null || this.activeOption.equals(activeOption)) {
            return;
        }

        this.activeOption = activeOption;
        refreshPhysicalEvents();
        fireActiveOptionChanged(this.activeOption);
    }

    /**
     * Sets the one and only filter on the PEM, meaning that existing filters
     * will first be cleared, and this new filter will be added.
     *
     * @param filter
     *            null means no filter please
     */
    public void setFilter(PhysicalEventType filter) {

        if (filter == null) {
            if (typeFilters.isEmpty()) {
                return;
            } else {
                typeFilters.clear();
                refreshPhysicalEvents();
                fireFiltersChanged(typeFilters);
                return;
            }
        }

        if (typeFilters.size() == 1 && typeFilters.contains(filter)) {
            return;
        } else {
            typeFilters.clear();
            typeFilters.add(filter);
        }
        refreshPhysicalEvents();
        fireFiltersChanged(typeFilters);
    }

    public void addFilter(PhysicalEventType type) {
        if (type == null) {
            throw new IllegalArgumentException(getClass().getName()
                    + " addFilter( f ) received a null filter.");
        }

        if (typeFilters.contains(type)) {
            return;
        }

        typeFilters.add(type);
        refreshPhysicalEvents();
        fireFiltersChanged(typeFilters);
    }

    public void removeFilter(PhysicalEventType type) {
        if (type == null) {
            throw new IllegalArgumentException(getClass().getName()
                    + " removeFilter( f ) received a null filter.");
        }

        if (!typeFilters.contains(type)) {
            return;
        }

        typeFilters.remove(type);
        refreshPhysicalEvents();
        fireFiltersChanged(typeFilters);
    }

    public void clearFilters() {
        if (typeFilters.isEmpty()) {
            return;
        }

        typeFilters.clear();
        refreshPhysicalEvents();
        fireFiltersChanged(typeFilters);
    }

    public List<PhysicalEventType> getFilters() {
        return Collections.unmodifiableList(typeFilters);
    }

    private boolean filtersAllow(PhysicalEventType type) {

        if (typeFilters.isEmpty() || typeFilters.contains(type)) {
            return true;
        }
        return false;
    }

    /**
     * The PEM will record a notion of "selected" PhysicalEvent IDs for use by
     * the UI. The updating of what is or isnt selected is up to the caller. So
     * if the PEM's filters or timeRange etc changes, the PEM will NOT update
     * this list of selected PhysicalEventIDs.
     *
     * @param mode
     */
    public void setSelectionMode(SelectionMode mode) {
        if (mode == null) {
            return;
        }

        selectionMode = mode;
        if (SelectionMode.SINGLE.equals(mode) && selectedEventIds.size() > 1) {
            selectedEventIds.clear();
            fireSelectedChanged(selectedEventIds);
        }
    }

    public SelectionMode getSelectionMode() {
        return selectionMode;
    }

    public boolean isSelected(String customEventId) {
        if (customEventId == null || customEventId.isEmpty()) {
            return false;
        }

        return selectedEventIds.contains(customEventId);
    }

    public boolean isSelected(IPhysicalEvent event) {
        if (event == null) {
            return false;
        }

        return isSelected(event.getCustomId());
    }

    /**
     * Passing null means to unselect everything.
     *
     * @param customEventId
     *            null to unselect all
     */
    public void setSelected(String customEventId) {

        if (customEventId != null && customEventId.isEmpty()) {
            return;
        }

        // If they want us to clear the selections...
        if (customEventId == null) {
            if (selectedEventIds.isEmpty()) {
                return;
            } else {
                selectedEventIds.clear();
                fireSelectedChanged(selectedEventIds);
                return;
            }
        }

        if (!selectedEventIds.contains(customEventId)) {
            if (SelectionMode.SINGLE.equals(selectionMode)) {
                selectedEventIds.clear();
            }
            selectedEventIds.add(customEventId);
            fireSelectedChanged(selectedEventIds);
        }
    }

    public void setSelected(IPhysicalEvent event) {
        if (event == null) {
            clearSelected();
        } else {
            setSelected(event.getCustomId());
        }
    }

    public void removeSelected(String customId) {

        boolean changed = false;
        Iterator<String> idIter = selectedEventIds.iterator();
        while (idIter.hasNext()) {
            String selectedId = idIter.next();
            if (selectedId.equals(customId)) {
                idIter.remove();
                changed = true;
                break;
            }
        }
        if (changed) {
            fireSelectedChanged(selectedEventIds);
        }
    }

    public void clearSelected() {
        if (selectedEventIds.isEmpty()) {
            return;
        }

        selectedEventIds.clear();
        fireSelectedChanged(selectedEventIds);
    }

    public Set<String> getSelected() {
        return Collections.unmodifiableSet(selectedEventIds);
    }

    public Set<IPhysicalEvent> getSelectedPhysicalEvents() {
        Set<IPhysicalEvent> selectedEvents = new HashSet<>();
        for (String selectedId : selectedEventIds) {
            IPhysicalEvent selectedEvent = getPhysicalEvent(selectedId);
            if (selectedEvent != null) {
                selectedEvents.add(selectedEvent);
            }
        }
        return selectedEvents;
    }

    /*
     * =========================================================================
     * PhysicalEvent Getter / Retrieval methods.
     * =========================================================================
     */

    /**
     * Requeries and refreshes the cache with physical events that satisfy the
     * PEM's constraints / properties, including the filters, timeWindow, and
     * active flag. Calls firePhysicalEventChanged if the event set has changed.
     */
    private void refreshPhysicalEvents() {

        isCacheInitialized = true;

        Map<PhysicalEventType, List<IPhysicalEvent>> oldEvents = phyEventCache;
        Map<PhysicalEventType, List<IPhysicalEvent>> newEvents = new HashMap<>();

        /*
         * Re-retrieve filtered physical events with the PEM's constraints. Go
         * thru each of the DAOs...
         */
        for (Map.Entry<PhysicalEventType, IPhysicalEventDao> entry : daoMap
                .entrySet()) {

            /*
             * Retrieve only the filtered PhysicalEventTypes
             */
            if (filtersAllow(entry.getKey())) {
                List<IPhysicalEvent> newEventsForType = entry.getValue()
                        .getPhysicalEvents(activeOption, timeWindow);
                newEvents.put(entry.getKey(), newEventsForType);
            }
        }

        /**
         * TODO Check if the new set is different than the old, and if so, set
         * the new set, and fire notification.
         *
         * For each old event, if it's not in the new set, then it's been
         * removed. So remove it from the old set and fireRemoved. Now what's
         * left in the old set is also in the new set.
         *
         * Go thru the each event in the new set, and if it's in the old, then
         * see if it has changed and fireChanged. If it's in the new but not in
         * the old, then it's new and fireAdded.
         */
        phyEventCache = newEvents;

        firePhysicalEventChanged(null, null);

        /**
         * Check if the selected events are still valid
         */
        for (String selectedEventId : getSelected()) {
            if (!cacheContains(selectedEventId)) {
                removeSelected(selectedEventId);
            }
        }
    }

    private boolean cacheContains(String customId) {

        if (customId == null || customId.isEmpty()) {
            return false;
        }

        for (Map.Entry<PhysicalEventType, List<IPhysicalEvent>> entry : phyEventCache
                .entrySet()) {

            List<IPhysicalEvent> cachedEvents = entry.getValue();
            if (cachedEvents == null) {
                continue;
            }

            for (IPhysicalEvent event : cachedEvents) {
                if (event.getCustomId().equals(customId)) {
                    return true;
                }
            }
        }
        return false;
    }

    /**
     * NOTE: Deletes by customId
     *
     * @param event
     */
    private boolean removeFromCache(String customId) {

        if (customId == null || customId.isEmpty()) {
            return false;
        }

        if (!isCacheInitialized) {
            refreshPhysicalEvents();
        }

        /*
         * Just go thru em all, and delete an existing one with the same id if
         * we find one.
         */
        boolean removed = false;
        for (Map.Entry<PhysicalEventType, List<IPhysicalEvent>> entry : phyEventCache
                .entrySet()) {

            List<IPhysicalEvent> cachedEvents = entry.getValue();

            // Delete any old ones by customId
            Iterator<IPhysicalEvent> cachedEventsIter = cachedEvents.iterator();
            while (cachedEventsIter.hasNext()) {
                IPhysicalEvent cachedEvent = cachedEventsIter.next();
                if (cachedEvent.getCustomId().equals(customId)) {
                    // Remove the old one
                    cachedEventsIter.remove();
                    removed = true;
                    break;
                }
            }
            if (removed) {
                removeSelected(customId);
            }
        }
        return removed;
    }

    private void addToCache(IPhysicalEvent event) {

        if (event == null) {
            return;
        }

        if (!isCacheInitialized) {
            refreshPhysicalEvents();
        }

        // Add the event
        List<IPhysicalEvent> cachedEvents = phyEventCache
                .get(event.getEventType());
        if (cachedEvents == null) {
            cachedEvents = new ArrayList<>();
            phyEventCache.put(event.getEventType(), cachedEvents);
        }
        cachedEvents.add(event);
    }

    /**
     * Returns a Set of all {@link PhysicalEventType} that the PEM is configured
     * for. See {@link PEMVizBundleActivator} for how the PEM gets configured
     * with DAOs.
     *
     * @return
     */
    public Set<PhysicalEventType> getPhysicalEventTypes() {

        SortedSet<PhysicalEventType> sortedSet = new TreeSet<>(daoMap.keySet());
        return sortedSet;
    }

    /**
     * Returns a Map of PhysicalEventType to customIds for the PhysicalEvents
     * contained in the PEM, that conform to the PEM's constraint properties,
     * such as the timeRange, activeOnly, and Filters.
     *
     * @return
     */
    public Map<PhysicalEventType, List<String>> getPhysicalEventIds() {

        if (!isCacheInitialized) {
            refreshPhysicalEvents();
        }

        Map<PhysicalEventType, List<String>> result = new HashMap<>();
        for (Map.Entry<PhysicalEventType, List<IPhysicalEvent>> entry : phyEventCache
                .entrySet()) {
            List<String> ids = new ArrayList<>();
            result.put(entry.getKey(), ids);
            for (IPhysicalEvent event : entry.getValue()) {
                ids.add(event.getCustomId());
            }
        }
        return result;
    }

    /**
     * Returns a list of customIds for the PhysicalEvents of the given type
     * contained in the PEM, that conform to the PEM's constraint properties,
     * such as the timeRange, activeOnly, and Filters.
     *
     * @return
     */
    public List<String> getPhysicalEventIds(PhysicalEventType type) {

        if (!isCacheInitialized) {
            refreshPhysicalEvents();
        }

        List<String> result = new ArrayList<>();
        List<IPhysicalEvent> events = phyEventCache.get(type);
        if (events != null) {
            for (IPhysicalEvent e : events) {
                result.add(e.getCustomId());
            }
        }
        return result;
    }

    /**
     * Returns alphabetically sorted list of IDs from all Physical Events
     * currently in the PEM
     *
     * @return
     */
    public List<String> getPhysicalEventIdsList() {
        if (!isCacheInitialized) {
            refreshPhysicalEvents();
        }

        List<String> result = new LinkedList<>();

        for (Map.Entry<PhysicalEventType, List<IPhysicalEvent>> entry : phyEventCache
                .entrySet()) {
            result.addAll(getPhysicalEventIds(entry.getKey()));
        }

        Collections.sort(result);
        return result;
    }

    /**
     * Returns the PhysicalEvent identified by the customId and type, if it is
     * contained in the PEM.
     *
     * @return null if the PhysicalEvent is not contained in the PEM
     */
    public IPhysicalEvent getPhysicalEvent(String customId,
            PhysicalEventType type) {

        if (!isCacheInitialized) {
            refreshPhysicalEvents();
        }

        if (customId == null || customId.isEmpty()
                || phyEventCache.get(type) == null) {
            return null;
        }

        List<IPhysicalEvent> events = phyEventCache.get(type);
        for (IPhysicalEvent e : events) {
            if (e.getCustomId().equals(customId)) {
                return e;
            }
        }

        return null;
    }

    /**
     * Returns the PhysicalEvent identified by the customId, if it is contained
     * in the PEM.
     *
     * @return null if the PhysicalEvent is not contained in the PEM
     */
    public IPhysicalEvent getPhysicalEvent(String customId) {

        if (!isCacheInitialized) {
            refreshPhysicalEvents();
        }

        if (customId == null || customId.isEmpty()) {
            return null;
        }

        for (Map.Entry<PhysicalEventType, List<IPhysicalEvent>> entry : phyEventCache
                .entrySet()) {
            for (IPhysicalEvent e : entry.getValue()) {
                if (e.getCustomId().equals(customId)) {
                    return e;
                }
            }
        }

        return null;
    }

    /**
     * Returns the PhysicalEvent identified by the customId and type, whether or
     * not it is contained in the PEM. Note that this will check the cache
     * first, and if not found, the physical event will be retrieved from the
     * database/edex without regard for the PEM's constraints. This allows
     * clients to, for example, retrieve inactive events even though the PEM
     * might be constrained to ACTIVE_ONLY. Though the DAOs can do this already,
     * providing this method alleviates clients from using the DAOs directly.
     *
     * @return null if the PhysicalEvent does not exist.
     */
    public IPhysicalEvent retrievePhysicalEvent(String customId,
            PhysicalEventType type) {

        if (!isCacheInitialized) {
            refreshPhysicalEvents();
        }

        if (customId == null || customId.isEmpty() || type == null) {
            return null;
        }

        /*
         * Check the cache first
         */
        List<IPhysicalEvent> cachedEvents = phyEventCache.get(type);
        if (cachedEvents != null) {
            for (IPhysicalEvent e : cachedEvents) {
                if (e.getCustomId().equals(customId)) {
                    return e;
                }
            }
        }

        /*
         * The cache does not have it, so use a DAO to retrieve it
         */
        IPhysicalEventDao dao = daoMap.get(type);
        if (dao == null) {
            return null;
        }

        return dao.getPhysicalEvent(customId);
    }

    /**
     * Returns the PhysicalEvents of the given type, if they are contained in
     * the PEM.
     *
     * @return empty list if the PhysicalEvents are not contained in the PEM, or
     *         a partial list for the one that are found.
     */
    public List<IPhysicalEvent> getPhysicalEvents(PhysicalEventType type) {

        if (!isCacheInitialized) {
            refreshPhysicalEvents();
        }

        List<IPhysicalEvent> result = new ArrayList<>();

        if (phyEventCache.get(type) == null) {
            return result;
        }

        List<IPhysicalEvent> events = phyEventCache.get(type);
        result.addAll(events);

        return result;
    }

    /**
     * Returns the PhysicalEvents contained in the PEM.
     *
     * @return Map by PhysicalEventType to (possibly empty) list of
     *         PhysicalEvents contained in the PEM.
     */
    public Map<PhysicalEventType, List<IPhysicalEvent>> getPhysicalEvents() {

        if (!isCacheInitialized) {
            refreshPhysicalEvents();
        }

        Map<PhysicalEventType, List<IPhysicalEvent>> result = new HashMap<>();

        for (Map.Entry<PhysicalEventType, List<IPhysicalEvent>> entry : phyEventCache
                .entrySet()) {
            List<IPhysicalEvent> events = new ArrayList<>(entry.getValue());
            result.put(entry.getKey(), events);
        }
        return result;
    }

    /**
     * Returns the PhysicalEvents contained in the PEM.
     *
     * @return list of the PhysicalEvents, unordered
     */
    public List<IPhysicalEvent> getPhysicalEventsList() {

        if (!isCacheInitialized) {
            refreshPhysicalEvents();
        }

        List<IPhysicalEvent> result = new LinkedList<>();

        for (Map.Entry<PhysicalEventType, List<IPhysicalEvent>> entry : phyEventCache
                .entrySet()) {
            result.addAll(entry.getValue());
        }
        return result;
    }

    public boolean savePhysicalEvent(IPhysicalEvent event) {

        if (event == null || event.getEventType() == null) {
            return false;
        }
        PhysicalEventType type = event.getEventType();
        IPhysicalEventDao dao = daoMap.get(type);
        if (dao != null) {
            try {
                dao.savePhysicalEvent(event);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        return false;
    }

    /*
     * =========================================================================
     * PEMListener and fireXYZ methods.
     * =========================================================================
     */
    public void addPEMListener(IPhysicalEventMgrListener lister) {
        if (lister == null) {
            return;
        }
        listeners.add(lister);
    }

    public boolean removePEMListener(IPhysicalEventMgrListener lister) {
        if (lister == null) {
            return false;
        }
        return listeners.remove(lister);
    }

    public void clearPEMListeners() {
        listeners.clear();
    }

    protected void firePhysicalEventAdded(String id, PhysicalEventType type) {
        if (id == null || type == null) {
            return;
        }
        for (IPhysicalEventMgrListener lister : listeners) {
            lister.physicalEventAdded(id, type);
        }
    }

    protected void firePhysicalEventChanged(String id, PhysicalEventType type) {
        if (id == null || type == null) {
            return;
        }
        for (IPhysicalEventMgrListener lister : listeners) {
            lister.physicalEventChanged(id, type);
        }
    }

    protected void firePhysicalEventRemoved(String id, PhysicalEventType type) {
        if (id == null || type == null) {
            return;
        }
        for (IPhysicalEventMgrListener lister : listeners) {
            lister.physicalEventRemoved(id, type);
        }
    }

    protected void fireTimeWindowChanged(TimeRange newTimeRange) {
        for (IPhysicalEventMgrListener lister : listeners) {
            // The new timeWindow
            lister.timeWindowChanged(
                    (newTimeRange != null ? newTimeRange.clone() : null));
        }
    }

    protected void fireActiveOptionChanged(ActiveOption activeOption) {
        for (IPhysicalEventMgrListener lister : listeners) {
            // The new activeOnly
            lister.activeOptionChanged(activeOption);
        }
    }

    protected void fireFiltersChanged(List<PhysicalEventType> newTypeFilters) {
        if (newTypeFilters == null) {
            return;
        }

        for (IPhysicalEventMgrListener lister : listeners) {
            // The new filters
            lister.filtersChanged(Collections.unmodifiableList(typeFilters));
        }
    }

    protected void fireSelectedChanged(Set<String> newSelections) {
        if (newSelections == null) {
            return;
        }
        for (IPhysicalEventMgrListener lister : listeners) {
            // The new selections
            lister.selectionsChanged(
                    Collections.unmodifiableSet(newSelections));
        }
    }

    /*
     * ========================================================================
     * DAO and IPhysicalEventDaoListener methods.
     * ========================================================================
     */
    public void addPhysicalEventDao(PhysicalEventType type,
            IPhysicalEventDao dao) {
        if (type == null || dao == null) {
            return;
        }
        dao.setPhysicalEventType(type);
        dao.addPhysicalEventDaoListener(daoListener);
        daoMap.put(type, dao);
    }

    public boolean removePhysicalEventDao(PhysicalEventType type) {
        IPhysicalEventDao dao = daoMap.remove(type);
        if (dao == null) {
            return false;
        }
        dao.removePhysicalEventDaoListener(daoListener);
        return true;
    }

    public void clearPhysicalEventDaos() {
        for (IPhysicalEventDao dao : daoMap.values()) {
            dao.removePhysicalEventDaoListener(daoListener);
        }
        daoMap.clear();
    }

    public IPhysicalEventDao getPhysicalEventDao(PhysicalEventType type) {
        if (type == null) {
            return null;
        }

        return daoMap.get(type);
    }

    /*
     * PhysicalEventDaoListener
     *
     * @TODO I dont think this is threadsafe, since Im guessing EDEX may notify
     * the DAOs on different threads, thereby entering these methods on
     * different threads.
     */
    private class PhysicalEventDaoListener
            implements IPhysicalEventDaoListener {

        /**
         * Only caches if the new or changed event satisfies the PEM's
         * constraints. If the event does not satisfy the PEM's constraints,
         * we'll remove it from the cache.
         *
         * @param id
         * @param type
         */
        private void retrieveAndAdjustCache(String id, PhysicalEventType type) {

            /*
             * If we dont have a DAO for the type, then we dont need to cache or
             * notify. NOTE If an old event with the same ID had a valid type,
             * then it will remain in the cache, and Im not sure if that's
             * correct behavior. Also, ignore filters for now, since the new
             * event maybe with a filter-disallowed type may be replacing an old
             * event (with the same id) that has a filter-allowed type, and
             * hence, we would need to remove it from our cache.
             */
            IPhysicalEventDao dao = daoMap.get(type);
            if (dao == null) {
                return;
            }

            // Otherwise, retrieve the event if it fits within the PEM's
            // active and time constraints, and add or replace in the cache
            List<String> customId = new ArrayList<>();
            customId.add(id);
            List<IPhysicalEvent> newOrUpdatedEvents = dao.getPhysicalEvents(
                    getActiveOption(), getTimeWindow(), customId);

            /**
             * If we didn't retrieve the event, remove it from the cache because
             * either there was a problem or the event doesnt satisfy the active
             * option or time window. If we have more than one event retrieved,
             * then that is an error.
             */
            if (newOrUpdatedEvents == null || newOrUpdatedEvents.isEmpty()) {
                removeFromCache(id);
                return;
            } else if (newOrUpdatedEvents.size() > 1) {
                return;
            }
            IPhysicalEvent newOrUpdatedEvent = newOrUpdatedEvents.get(0);

            /*
             * Remove first, and then add if appropriate. Remove also removes
             * the selected-ness, and so re-select if added.
             */
            boolean wasSelected = isSelected(id);
            removeFromCache(newOrUpdatedEvent.getCustomId());
            if (filtersAllow(newOrUpdatedEvent.getEventType())) {
                addToCache(newOrUpdatedEvent);
                if (wasSelected) {
                    setSelected(id);
                }
            }
        }

        @Override
        public void physicalEventAdded(String id, PhysicalEventType type) {
            retrieveAndAdjustCache(id, type);
            firePhysicalEventAdded(id, type);
        }

        /**
         * This is our notification from EDEX, that a new or changed event
         * exists on the server. So if it satisfies the PEM's properties (ie
         * typeFilters, timeWindow, activeOption), then retrieve the event from
         * EDEX and add or replace it in our cache.
         */
        @Override
        public void physicalEventChanged(String id, PhysicalEventType type) {
            retrieveAndAdjustCache(id, type);
            firePhysicalEventChanged(id, type);
        }

        @Override
        public void physicalEventRemoved(String id, PhysicalEventType type) {

            if (!isCacheInitialized) {
                refreshPhysicalEvents();
            }

            // Add or replace by customId
            boolean removed = removeFromCache(id);
            if (removed) {
                firePhysicalEventRemoved(id, type);
            }
        }

    }

}
