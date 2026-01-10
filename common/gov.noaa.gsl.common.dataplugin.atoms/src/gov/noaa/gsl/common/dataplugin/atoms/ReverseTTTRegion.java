package gov.noaa.gsl.common.dataplugin.atoms;

/**
 * Normally I would make this an enum in the ReverseTTTUtilities class and the
 * ReverseTTTRequest, ReverseTTTResponse, ReverseTTTRequestHandler, and
 * ReverseTTTClientUtilities classes would depend on it, and of course this
 * would all go in the edex plugin. Yet I don't want the Request/Response to
 * depend on the edex plugin. So it's a quandary. I can't think of anywhere
 * better to put it, in that case, other than here.
 *
 * @author awips
 *
 */
public enum ReverseTTTRegion {

    HAWAII,
    AMSAM,
    GUAM,
    PRVI
}
